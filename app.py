import base64
import html
import io
import json
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
import streamlit as st
from docx import Document
from docx.shared import Inches
from streamlit.runtime.secrets import StreamlitSecretNotFoundError

# 版本信息
VERSION = "1.0"

# 飞书多维表格配置（支持环境变量覆盖）
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN", "NO9nbcpjraKeUCsSQkBcHL9gnhh")
TABLE_ID = os.getenv("FEISHU_TABLE_ID", "tblchSd315sqHTCt")


@st.cache_data(show_spinner=False, ttl=50 * 60)
def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """
    获取 tenant_access_token，用于后续调用多维表格接口。
    """
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"获取 tenant_access_token 失败: {data}")
    return data["tenant_access_token"]


def fetch_records(token: str) -> List[Dict]:
    """
    拉取表格全部记录，自动翻页。
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search"
    headers = {"Authorization": f"Bearer {token}"}
    page_token = None
    records: List[Dict] = []

    while True:
        payload: Dict[str, object] = {"page_size": 100}
        if page_token:
            payload["page_token"] = page_token

        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if not resp.ok:
            # 返回更友好的错误信息，便于排查 token/table 权限问题
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise RuntimeError(f"拉取记录失败 HTTP {resp.status_code}: {detail}")
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"拉取记录失败: {data}")

        items = data["data"].get("items", [])
        records.extend(items)
        page_token = data["data"].get("page_token")

        if not data["data"].get("has_more"):
            break

    return records


def normalize_to_list(value) -> List[str]:
    """
    将单值或列表字段统一转成字符串列表。
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v is not None]
    return [str(value)]


def normalize_text(value) -> str:
    """
    将字段安全转换为字符串；列表会合并成换行分隔。
    """
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join([str(v) for v in value if v is not None]).strip()
    return str(value).strip()


def is_image_file(name: str, mime: str = None) -> bool:
    """
    判断是否为图片文件（根据MIME类型或文件扩展名）。
    """
    if mime:
        return mime.startswith("image/")
    if name:
        ext = name.lower().split(".")[-1] if "." in name else ""
        return ext in ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"]
    return False


def extract_attachments(value) -> List[Dict]:
    """
    提取附件列表，兼容飞书多维表格附件字段常见结构。
    """
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if not isinstance(item, dict):
            continue
        url = item.get("download_url") or item.get("tmp_url") or item.get("url")
        name = item.get("name") or item.get("file_name") or "附件"
        mime = item.get("mime_type") or item.get("type")
        result.append({"name": name, "url": url, "mime": mime})
    return result


def parse_records(raw_records: List[Dict]) -> List[Dict]:
    """
    将飞书接口返回的记录解析为标准结构。
    """
    parsed = []
    for item in raw_records:
        fields = item.get("fields", {})
        subject = fields.get("学科")
        knowledge_points = normalize_to_list(fields.get("知识点"))
        reason_type = normalize_text(fields.get("不会/做错"))
        reason_detail = normalize_text(fields.get("不会/做错原因"))
        
        # 处理"去手写"字段：优先作为附件处理，否则作为文本
        handwriting_raw = fields.get("去手写")
        attachments = extract_attachments(handwriting_raw)
        handwriting_text = ""
        # 如果不是附件列表，则作为文本处理
        if not attachments:
            handwriting_text = normalize_text(handwriting_raw)
        
        # 获取创建时间（飞书API返回的是毫秒时间戳）
        created_time = item.get("created_time", 0)
        if isinstance(created_time, str):
            try:
                created_time = int(created_time)
            except ValueError:
                created_time = 0

        record_id = item.get("record_id") or ""

        parsed.append(
            {
                "record_id": record_id,
                "subject": subject,
                "knowledge_points": knowledge_points,
                "handwriting_text": handwriting_text,
                "reason_type": reason_type,
                "reason_detail": reason_detail,
                "attachments": attachments,
                "created_time": created_time,  # 毫秒时间戳
            }
        )
    return parsed


# ----- 错题练习：练习记录表与选题 -----
# 练习记录表字段名（与飞书多维表格中新建表一致）
_P_FIELD_RID = "错题record_id"
_P_FIELD_LAST = "上次练习时间"
_P_FIELD_MASTERY = "掌握程度"
_P_FIELD_COUNT = "练习次数"
_P_FIELD_NEXT = "下次练习时间"


def _interval_days_for_mastered(n: int) -> int:
    """「会」时按练习次数给出的间隔天数。"""
    return {1: 1, 2: 3, 3: 7, 4: 14}.get(n, 30)


def fetch_practice_records(token: str, practice_table_id: str) -> Dict[str, Dict[str, Any]]:
    """
    拉取练习记录表全部记录，返回 错题record_id -> {practice_record_id, 上次练习时间, 掌握程度, 练习次数, 下次练习时间}。
    同一错题若有多条，保留 上次练习时间 最大的一条。
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{practice_table_id}/records/search"
    headers = {"Authorization": f"Bearer {token}"}
    page_token = None
    out: Dict[str, Dict[str, Any]] = {}

    while True:
        payload: Dict[str, object] = {"page_size": 100}
        if page_token:
            payload["page_token"] = page_token
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if not resp.ok:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise RuntimeError(f"拉取练习记录失败 HTTP {resp.status_code}: {detail}")
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"拉取练习记录失败: {data}")

        for item in data.get("data", {}).get("items", []):
            fields = item.get("fields", {})
            rid = (fields.get(_P_FIELD_RID) or "").strip() or None
            if not rid:
                continue
            try:
                last_ms = int(fields.get(_P_FIELD_LAST) or 0)
            except (TypeError, ValueError):
                last_ms = 0
            try:
                cnt = int(fields.get(_P_FIELD_COUNT) or 0)
            except (TypeError, ValueError):
                cnt = 0
            try:
                next_ms = int(fields.get(_P_FIELD_NEXT) or 0)
            except (TypeError, ValueError):
                next_ms = 0
            mastery = (fields.get(_P_FIELD_MASTERY) or "").strip() or "不会"

            # 若已存在，只保留 上次练习时间 更大的一条
            if rid in out and (out[rid].get(_P_FIELD_LAST) or 0) >= last_ms:
                continue
            out[rid] = {
                "practice_record_id": item.get("record_id"),
                _P_FIELD_LAST: last_ms,
                _P_FIELD_MASTERY: mastery,
                _P_FIELD_COUNT: cnt,
                _P_FIELD_NEXT: next_ms,
            }

        page_token = data.get("data", {}).get("page_token")
        if not data.get("data", {}).get("has_more"):
            break

    return out


def create_practice_record(
    token: str,
    practice_table_id: str,
    question_record_id: str,
    mastery: str,
    count: int,
    next_ts_ms: int,
) -> Optional[str]:
    """在练习记录表中新建一条记录，返回新记录的 record_id。"""
    now_ms = int(time.time() * 1000)
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{practice_table_id}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "fields": {
            _P_FIELD_RID: question_record_id,
            _P_FIELD_LAST: now_ms,
            _P_FIELD_MASTERY: mastery,
            _P_FIELD_COUNT: count,
            _P_FIELD_NEXT: next_ts_ms,
        }
    }
    resp = requests.post(url, headers=headers, json=body, timeout=10)
    if not resp.ok:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"创建练习记录失败 HTTP {resp.status_code}: {detail}")
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"创建练习记录失败: {data}")
    rec = (data.get("data") or {}).get("record") or {}
    return rec.get("record_id")


def update_practice_record(
    token: str,
    practice_table_id: str,
    practice_record_id: str,
    mastery: str,
    count: int,
    next_ts_ms: int,
) -> None:
    """更新练习记录表中一条记录。"""
    now_ms = int(time.time() * 1000)
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{practice_table_id}/records/{practice_record_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "fields": {
            _P_FIELD_LAST: now_ms,
            _P_FIELD_MASTERY: mastery,
            _P_FIELD_COUNT: count,
            _P_FIELD_NEXT: next_ts_ms,
        }
    }
    resp = requests.put(url, headers=headers, json=body, timeout=10)
    if not resp.ok:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"更新练习记录失败 HTTP {resp.status_code}: {detail}")
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"更新练习记录失败: {data}")


def pick_next_question(
    filtered: List[Dict],
    practice_map: Dict[str, Dict[str, Any]],
    now_ms: int,
) -> Optional[Dict]:
    """
    从筛选后的错题中选一道：下次练习时间<=now 优先，否则取下次练习时间最早；无练习记录视为 0 最优先。
    """
    def next_ts(r: Dict) -> int:
        rid = (r.get("record_id") or "").strip()
        if not rid:
            return 0
        p = practice_map.get(rid)
        return int(p.get(_P_FIELD_NEXT, 0) or 0) if p else 0

    # 过滤：至少有 record_id、且 去手写 或 附件 非空
    cand = [r for r in filtered if (r.get("record_id") or "").strip() and (r.get("handwriting_text") or r.get("attachments"))]
    if not cand:
        return None

    # 排序：下次练习时间 <= now 的优先；否则按 下次练习时间 升序
    cand.sort(key=lambda r: (0 if next_ts(r) <= now_ms else 1, next_ts(r)))
    return cand[0]


def save_practice_feedback(
    token: str,
    practice_table_id: str,
    question_record_id: str,
    mastered: bool,
    practice_map: Dict[str, Dict[str, Any]],
) -> None:
    """
    根据用户选择 会/不会 写入或更新练习记录，并就地更新 practice_map 以便本地选题正确。
    mastered=True 表示「会」，False 表示「不会」。
    """
    now_ms = int(time.time() * 1000)
    p = practice_map.get(question_record_id) if question_record_id else None
    prev_count = int(p.get(_P_FIELD_COUNT, 0) or 0) if p else 0
    count = prev_count + 1
    mastery = "会" if mastered else "不会"

    if mastered:
        days = _interval_days_for_mastered(count)
        next_ts_ms = now_ms + days * 24 * 60 * 60 * 1000
    else:
        next_ts_ms = now_ms + 5 * 60 * 1000  # +5 分钟

    if p and p.get("practice_record_id"):
        update_practice_record(token, practice_table_id, p["practice_record_id"], mastery, count, next_ts_ms)
        p[_P_FIELD_LAST] = now_ms
        p[_P_FIELD_MASTERY] = mastery
        p[_P_FIELD_COUNT] = count
        p[_P_FIELD_NEXT] = next_ts_ms
    else:
        new_id = create_practice_record(token, practice_table_id, question_record_id, mastery, count, next_ts_ms)
        practice_map[question_record_id] = {
            "practice_record_id": new_id,
            _P_FIELD_LAST: now_ms,
            _P_FIELD_MASTERY: mastery,
            _P_FIELD_COUNT: count,
            _P_FIELD_NEXT: next_ts_ms,
        }


def _load_image_bytes_for_display(url: str, token: str) -> Optional[bytes]:
    """下载附件图片用于 Streamlit 展示，支持飞书临时 JSON。"""
    if not url or not token:
        return None
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if not r.ok:
            return None
        ct = (r.headers.get("Content-Type") or "").lower()
        if "application/json" in ct:
            try:
                j = r.json()
                if isinstance(j, dict) and j.get("code") == 0:
                    d = j.get("data", {})
                    u = None
                    tmp = d.get("tmp_download_urls") or []
                    if tmp and isinstance(tmp, list) and tmp:
                        u = tmp[0].get("tmp_download_url") if isinstance(tmp[0], dict) else None
                    if not u:
                        u = d.get("tmp_download_url") or d.get("download_url")
                    if u:
                        r2 = requests.get(u, headers=headers, timeout=15, allow_redirects=True)
                        if r2.ok:
                            return r2.content
            except Exception:
                pass
        return r.content if r.content else None
    except Exception:
        return None


def render_question_streamlit(record: Dict, token: str) -> None:
    """在 Streamlit 中渲染一道题的文本与图片。"""
    t = (record.get("handwriting_text") or "").strip()
    if t:
        st.markdown(t)
    for att in (record.get("attachments") or []):
        if not is_image_file(att.get("name"), att.get("mime")):
            continue
        url = att.get("url")
        raw = _load_image_bytes_for_display(url, token)
        if raw:
            try:
                st.image(io.BytesIO(raw))
            except Exception:
                pass


def safe_get_secret(key: str):
    """
    安全读取 st.secrets，避免未配置 secrets.toml 时抛出异常。
    在 Streamlit Cloud 上，secrets 通过 st.secrets 字典直接访问。
    """
    try:
        # 直接使用最简单的方式：st.secrets.get(key)
        # 这是 Streamlit 推荐的标准方式，在所有环境下都可用
        value = st.secrets.get(key)
        # 如果返回空字符串，也视为未配置
        if value == "" or value is None:
            return None
        return value
    except (StreamlitSecretNotFoundError, AttributeError):
        # 如果 st.secrets 不存在或未配置，返回 None
        return None
    except KeyError:
        # 如果 key 不存在，返回 None（get 方法不会抛出 KeyError，但为了安全还是捕获）
        return None
    except Exception:
        # 其他异常，返回 None
        return None


def get_config_file_path() -> Path:
    """
    获取配置文件路径（在项目目录下的 .feishu_config.json）。
    """
    return Path(__file__).parent / ".feishu_config.json"


def load_config() -> Dict[str, Optional[str]]:
    """
    从本地配置文件加载凭据。
    """
    config_file = get_config_file_path()
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(app_id: str, app_secret: str) -> None:
    """
    保存凭据到本地配置文件。
    注意：在 Streamlit Cloud 等只读文件系统上，此操作会静默失败。
    """
    config_file = get_config_file_path()
    try:
        config = {"FEISHU_APP_ID": app_id, "FEISHU_APP_SECRET": app_secret}
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        # 设置文件权限（仅所有者可读写）
        if os.name != "nt":  # 非Windows系统
            os.chmod(config_file, 0o600)
    except (IOError, OSError, PermissionError):
        # 在 Streamlit Cloud 等只读文件系统上，保存失败是正常的
        # 配置应通过环境变量或 st.secrets 提供
        pass
    except Exception:
        pass  # 其他错误也静默处理


def build_doc(subjects: List[str], selections: Dict[str, List[Dict]], token: str) -> bytes:
    """
    根据选择生成 Word 文档二进制内容。
    """
    doc = Document()
    title = "、".join(subjects) if subjects else "错题"
    doc.add_heading(f"{title} 错题专项训练", 0)

    for kp, questions in selections.items():
        # 跳过空列表（生成失败的题目）
        if not questions:
            continue
        doc.add_heading(kp, level=1)
        for idx, q in enumerate(questions, start=1):
            # 题目内容：优先使用附件（图片），否则使用文本
            attachments = q.get("attachments") or []
            handwriting_text = q.get("handwriting_text", "").strip()
            
            if attachments:
                # 有附件，直接插入图片（使用Word自动编号）
                para = doc.add_paragraph(style="List Number")
                
                # 处理所有附件
                for att in attachments:
                    url = att.get("url")
                    name = att.get("name") or "附件"
                    mime = att.get("mime")
                    if not url:
                        continue
                    
                    # 先判断是否为图片（优先使用mime，其次文件名扩展名）
                    is_image = is_image_file(name, mime)
                    
                    if not is_image:
                        # 如果不是图片，直接给出链接
                        doc.add_paragraph(f"附件：{name}（非图片，下载链接：{url}）").italic = True
                        continue
                    
                    try:
                        headers = {"Authorization": f"Bearer {token}"}
                        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                        if not resp.ok:
                            doc.add_paragraph(f"[附件下载失败] {name} - HTTP {resp.status_code}")
                            continue
                        
                        # 检查响应是否为JSON（飞书API可能返回JSON）
                        content_type = resp.headers.get("Content-Type", "").lower()
                        image_data = None
                        
                        # 如果Content-Type是JSON，尝试解析提取真实下载URL
                        if "application/json" in content_type:
                            try:
                                json_data = resp.json()
                                # 如果是JSON，尝试提取真实下载URL
                                if isinstance(json_data, dict) and json_data.get("code") == 0:
                                    data = json_data.get("data", {})
                                    # 尝试多种可能的URL字段
                                    tmp_urls = data.get("tmp_download_urls", [])
                                    if tmp_urls and isinstance(tmp_urls, list) and len(tmp_urls) > 0:
                                        real_url = tmp_urls[0].get("tmp_download_url") if isinstance(tmp_urls[0], dict) else None
                                    else:
                                        real_url = data.get("tmp_download_url") or data.get("download_url") or json_data.get("download_url")
                                    
                                    if real_url:
                                        # 使用真实URL重新下载
                                        resp2 = requests.get(real_url, headers=headers, timeout=15, allow_redirects=True)
                                        if resp2.ok:
                                            image_data = resp2.content
                                        else:
                                            doc.add_paragraph(f"[附件下载失败] {name} - HTTP {resp2.status_code}")
                                            continue
                                    else:
                                        # 无法提取真实URL
                                        doc.add_paragraph(f"[无法获取附件下载地址] {name}")
                                        continue
                            except (ValueError, KeyError, TypeError) as json_err:
                                # JSON解析失败，降级使用响应内容
                                image_data = resp.content
                        else:
                            # 不是JSON，直接使用响应内容作为图片数据
                            image_data = resp.content
                        
                        if image_data:
                            # 尝试插入图片
                            try:
                                image_stream = io.BytesIO(image_data)
                                doc.add_picture(image_stream, width=Inches(5.5))
                            except Exception as img_exc:  # noqa: BLE001
                                # 插入图片失败，可能是格式不支持
                                doc.add_paragraph(f"附件：{name}（图片插入失败：{img_exc}）").italic = True
                        else:
                            doc.add_paragraph(f"[附件处理失败] {name}")
                    except Exception as exc:  # noqa: BLE001
                        doc.add_paragraph(f"[附件处理异常] {name}: {exc}")
            elif handwriting_text:
                # 没有附件但有文本，显示文本
                para = doc.add_paragraph(style="List Number")
                para.add_run(handwriting_text)
            else:
                # 既无附件也无文本
                para = doc.add_paragraph(style="List Number")
                para.add_run("（无题干）")
            
            # 追加备注信息，便于回顾错因
            if q.get("reason_type") or q.get("reason_detail"):
                note = f"错因：{q.get('reason_type') or ''} {q.get('reason_detail') or ''}".strip()
                if note.startswith("错因："):
                    doc.add_paragraph(note).italic = True

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def build_html(subjects: List[str], selections: Dict[str, List[Dict]], token: str) -> str:
    """
    根据选择生成 HTML 文档内容。
    """
    title = "、".join(subjects) if subjects else "错题"
    
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='zh-CN'>",
        "<head>",
        "    <meta charset='UTF-8'>",
        "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        f"    <title>{title} 错题专项训练</title>",
        "    <style>",
        "        body { font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 1200px; margin: 0 auto; }",
        "        h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }",
        "        h2 { color: #555; margin-top: 30px; border-left: 5px solid #2196F3; padding-left: 15px; }",
        "        .question { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }",
        "        .question-number { font-weight: bold; color: #2196F3; margin-right: 10px; }",
        "        .question-content { margin: 10px 0; }",
        "        .question-content img { max-width: 100%; height: auto; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }",
        "        .reason { font-style: italic; color: #666; margin-top: 10px; padding-left: 20px; }",
        "        .error-note { color: #ff9800; font-size: 0.9em; }",
        "    </style>",
        "</head>",
        "<body>",
        f"    <h1>{title} 错题专项训练</h1>",
    ]
    
    for kp, questions in selections.items():
        # 跳过空列表（生成失败的题目）
        if not questions:
            continue
        html_parts.append(f"    <h2>{kp}</h2>")
        
        for idx, q in enumerate(questions, start=1):
            html_parts.append("    <div class='question'>")
            html_parts.append(f"        <div class='question-number'>{idx}.</div>")
            html_parts.append("        <div class='question-content'>")
            
            attachments = q.get("attachments") or []
            handwriting_text = q.get("handwriting_text", "").strip()
            
            if attachments:
                # 处理附件（图片）
                for att in attachments:
                    url = att.get("url")
                    name = att.get("name") or "附件"
                    mime = att.get("mime")
                    
                    if not url:
                        continue
                    
                    is_image = is_image_file(name, mime)
                    
                    if is_image:
                        try:
                            headers = {"Authorization": f"Bearer {token}"}
                            resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                            
                            if resp.ok:
                                content_type = resp.headers.get("Content-Type", "").lower()
                                image_data = None
                                final_content_type = content_type
                                
                                # 处理JSON响应
                                if "application/json" in content_type:
                                    try:
                                        json_data = resp.json()
                                        if isinstance(json_data, dict) and json_data.get("code") == 0:
                                            data = json_data.get("data", {})
                                            tmp_urls = data.get("tmp_download_urls", [])
                                            if tmp_urls and isinstance(tmp_urls, list) and len(tmp_urls) > 0:
                                                real_url = tmp_urls[0].get("tmp_download_url") if isinstance(tmp_urls[0], dict) else None
                                            else:
                                                real_url = data.get("tmp_download_url") or data.get("download_url")
                                            
                                            if real_url:
                                                resp2 = requests.get(real_url, headers=headers, timeout=15, allow_redirects=True)
                                                if resp2.ok:
                                                    image_data = resp2.content
                                                    final_content_type = resp2.headers.get("Content-Type", "image/png").lower()
                                    except Exception:
                                        pass
                                
                                if not image_data:
                                    image_data = resp.content
                                    final_content_type = content_type
                                
                                # 转换为base64嵌入
                                img_base64 = base64.b64encode(image_data).decode('utf-8')
                                img_src = f"data:{final_content_type or 'image/png'};base64,{img_base64}"
                                html_parts.append(f"            <img src='{img_src}' alt='{name}' />")
                            else:
                                html_parts.append(f"            <p class='error-note'>[图片加载失败] {name}</p>")
                        except Exception as exc:
                            html_parts.append(f"            <p class='error-note'>[图片加载异常] {name}: {exc}</p>")
                    else:
                        html_parts.append(f"            <p>附件：<a href='{url}' target='_blank'>{name}</a></p>")
            elif handwriting_text:
                # 显示文本内容（转义HTML特殊字符）
                escaped_text = html.escape(handwriting_text)
                html_parts.append(f"            <div>{escaped_text.replace(chr(10), '<br>')}</div>")
            else:
                html_parts.append("            <div>（无题干）</div>")
            
            html_parts.append("        </div>")
            
            # 添加错因备注
            if q.get("reason_type") or q.get("reason_detail"):
                reason = f"{q.get('reason_type') or ''} {q.get('reason_detail') or ''}".strip()
                if reason:
                    html_parts.append(f"        <div class='reason'>错因：{html.escape(reason)}</div>")
            
            html_parts.append("    </div>")
    
    html_parts.extend([
        "</body>",
        "</html>"
    ])
    
    return "\n".join(html_parts)


def generate_similar_questions_with_llm(reference_question: Dict, count: int, api_key: str, api_base: str = None, model: str = None, token: str = None) -> List[str]:
    """
    使用大模型生成类似题目。
    
    Args:
        reference_question: 参考题目（包含handwriting_text或attachments）
        count: 需要生成的题目数量
        api_key: API密钥
        api_base: API基础URL（智谱AI API Base URL）
        model: 模型名称（可选，如果不指定则根据api_base自动选择）
    
    Returns:
        生成的题目列表
    """
    # 构建参考题目的文本描述
    ref_text = reference_question.get("handwriting_text", "").strip()
    attachments = reference_question.get("attachments", [])
    
    if not ref_text and not attachments:
        raise ValueError("参考题目不能为空")
    
    # 检查是否有图片附件
    image_attachments = [att for att in attachments if is_image_file(att.get("name", ""), att.get("mime"))]
    has_images = len(image_attachments) > 0
    
    # 构建提示词
    if ref_text:
        question_description = ref_text
    elif has_images:
        question_description = "（请查看图片中的题目内容）"
    else:
        question_description = "[题目内容]"
    
    prompt_text = f"""你是一位经验丰富的教师，需要基于参考题目生成类似的新题目。

参考题目：{question_description}

请生成 {count} 道类似的题目，要求：

1. **保持核心要素一致**：
   - 保持相同的知识点和解题方法
   - 保持相同的题目类型（如选择题、填空题、计算题等）
   - 保持相同的难度级别
   - 如果是数学题，保持相同的运算类型和公式结构

2. **只改变可变要素**：
   - 可以改变具体数字、数值（如：把"5+3"改为"7+4"）
   - 可以改变具体的人物、物品、场景名称
   - 可以改变题目的表述方式，但核心意思保持一致
   - 保持题目的结构和解题步骤一致

3. **输出格式**：
   - 每道题目单独一行
   - 只输出题目内容，不要编号，不要添加"题目1"、"题目2"等前缀
   - 不要添加任何解释说明
   - 确保每道题目都是完整、独立、可以直接使用的

4. **质量要求**：
   - 题目必须合理、可解，不能出现逻辑错误
   - 题目必须与原题难度相当
   - 不能生成完全相同的题目，但也不能偏离太远
   - 生成的题目应该可以直接用于练习

请严格按照以上要求生成 {count} 道类似题目，每行一道："""
    
    # 默认使用智谱AI GLM-4.6V（支持多模态）
    if not model:
        model = "glm-4.6v"
    
    # 调用智谱AI API
    # 智谱AI的API URL格式
    if api_base and api_base.endswith("/chat/completions"):
        api_url = api_base
    else:
        api_url = (api_base or "https://open.bigmodel.cn/api/paas/v4").rstrip('/') + "/chat/completions"
    # 智谱AI的认证格式
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 检查模型是否支持多模态（图片输入）
    model_lower = (model or "").lower()
    supports_vision = (
        "4.6v" in model_lower or 
        "glm-4-6v" in model_lower or 
        "glm-4.6v" in model_lower or
        "vision" in model_lower or 
        "4o" in model_lower or
        "gpt-4o" in model_lower
    )
    
    # 构建消息内容
    if has_images and supports_vision:
        # 构建多模态消息（包含图片）
        content_list = []
        image_added = False
        
        # 添加图片
        for img_att in image_attachments[:1]:  # 只使用第一张图片
            img_url = img_att.get("url")
            if img_url and token:
                try:
                    # 下载图片并转换为base64
                    img_headers = {"Authorization": f"Bearer {token}"}
                    img_resp = requests.get(img_url, headers=img_headers, timeout=15, allow_redirects=True)
                    
                    if img_resp.ok:
                        # 检查是否是JSON响应（飞书的临时URL）
                        content_type = img_resp.headers.get("Content-Type", "").lower()
                        image_data = None
                        
                        if "application/json" in content_type:
                            try:
                                json_data = img_resp.json()
                                if isinstance(json_data, dict) and json_data.get("code") == 0:
                                    data = json_data.get("data", {})
                                    tmp_urls = data.get("tmp_download_urls", [])
                                    if tmp_urls and isinstance(tmp_urls, list) and len(tmp_urls) > 0:
                                        real_url = tmp_urls[0].get("tmp_download_url") if isinstance(tmp_urls[0], dict) else None
                                    else:
                                        real_url = data.get("tmp_download_url") or data.get("download_url")
                                    
                                    if real_url:
                                        img_resp2 = requests.get(real_url, headers=img_headers, timeout=15, allow_redirects=True)
                                        if img_resp2.ok:
                                            image_data = img_resp2.content
                            except Exception as e:
                                # 如果JSON解析失败，尝试直接使用响应内容
                                pass
                        
                        if not image_data:
                            image_data = img_resp.content
                        
                        if image_data and len(image_data) > 0:
                            # 转换为base64
                            img_base64 = base64.b64encode(image_data).decode('utf-8')
                            img_mime = img_att.get("mime") or content_type or "image/png"
                            # 确保MIME类型正确
                            if not img_mime or img_mime == "application/json":
                                img_mime = "image/png"
                            
                            content_list.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{img_mime};base64,{img_base64}"
                                }
                            })
                            image_added = True
                except Exception as e:
                    # 图片下载失败，记录错误但继续
                    pass
        
        # 添加文本提示
        content_list.append({
            "type": "text",
            "text": prompt_text
        })
        
        # 如果成功添加了图片，使用多模态消息；否则回退到纯文本
        if image_added:
            messages = [{"role": "user", "content": content_list}]
        else:
            # 图片添加失败，如果有文本内容，使用文本；否则抛出错误
            if ref_text:
                # 有文本内容，重新构建提示词（不提及图片）
                fallback_prompt = f"""你是一位经验丰富的教师，需要基于参考题目生成类似的新题目。

参考题目：{ref_text}

请生成 {count} 道类似的题目，要求：

1. **保持核心要素一致**：
   - 保持相同的知识点和解题方法
   - 保持相同的题目类型（如选择题、填空题、计算题等）
   - 保持相同的难度级别
   - 如果是数学题，保持相同的运算类型和公式结构

2. **只改变可变要素**：
   - 可以改变具体数字、数值（如：把"5+3"改为"7+4"）
   - 可以改变具体的人物、物品、场景名称
   - 可以改变题目的表述方式，但核心意思保持一致
   - 保持题目的结构和解题步骤一致

3. **输出格式**：
   - 每道题目单独一行
   - 只输出题目内容，不要编号，不要添加"题目1"、"题目2"等前缀
   - 不要添加任何解释说明
   - 确保每道题目都是完整、独立、可以直接使用的

4. **质量要求**：
   - 题目必须合理、可解，不能出现逻辑错误
   - 题目必须与原题难度相当
   - 不能生成完全相同的题目，但也不能偏离太远
   - 生成的题目应该可以直接用于练习

请严格按照以上要求生成 {count} 道类似题目，每行一道："""
                messages = [{"role": "user", "content": fallback_prompt}]
            else:
                # 没有文本也没有图片，无法生成题目
                raise ValueError("题目包含图片但图片处理失败，且没有文本内容，无法生成类似题目。请检查图片URL或网络连接。")
    else:
        # 纯文本消息
        messages = [{"role": "user", "content": prompt_text}]
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        # 检查响应状态
        if not response.ok:
            # 获取详细的错误信息
            try:
                error_detail = response.json()
                error_msg = f"API错误 {response.status_code}: {error_detail}"
            except:
                error_msg = f"API错误 {response.status_code}: {response.text[:200]}"
            
            # 根据不同错误码提供更详细的提示
            if response.status_code == 400:
                error_msg += f"\n请求URL: {api_url}\n模型: {model}\n请检查模型名称、API Key和请求格式是否正确。"
            elif response.status_code == 401:
                error_msg += f"\n请求URL: {api_url}\n模型: {model}\n⚠️ API Key无效或已过期，请检查：\n1. API Key是否正确\n2. API Key是否已过期\n3. API Key是否有足够的权限访问该模型"
            
            raise Exception(error_msg)
        
        response.raise_for_status()
        result = response.json()
        
        # 检查响应格式
        if "choices" not in result or not result["choices"]:
            raise Exception(f"API响应格式错误: {result}")
        
        # 提取生成的文本
        generated_text = result["choices"][0]["message"]["content"].strip()
        
        # 按行分割，过滤空行
        questions = [q.strip() for q in generated_text.split("\n") if q.strip()]
        
        # 如果生成的数量不够，重复最后一道题
        while len(questions) < count:
            questions.append(questions[-1] if questions else "（生成失败）")
        
        # 如果生成的数量太多，只取前count个
        return questions[:count]
    
    except Exception as e:
        # 如果API调用失败，抛出异常以便上层处理
        raise Exception(f"题目生成失败: {str(e)}")


def main() -> None:
    st.set_page_config(page_title="错题生成试卷", page_icon="📄", layout="wide")
    st.title("飞书错题本生成试卷")
    st.caption(f"v{VERSION} - 实现题库本身WORD文档")

    st.markdown(
        "从飞书多维表格自动读取学科与知识点，选择后生成可下载的 Word 文档或 HTML 文档。"
    )
    
    # 提示信息
    st.info("💡 提示：支持生成题库和类似题目，每种都支持 WORD 文档和 HTML 文档两种格式")
    st.caption(f"当前表：app_token={APP_TOKEN} · table_id={TABLE_ID}（可用环境变量覆盖）")

    # 读取密钥：优先环境变量/Secrets/配置文件/session state
    # 在 Streamlit Cloud 上，优先使用 secrets，不显示手动输入界面
    config = load_config()
    
    # 检测是否在 Streamlit Cloud 上运行
    # 方法：检查 st.secrets 是否可以访问
    # 在 Streamlit Cloud 上，st.secrets 对象总是存在（即使未配置 secrets）
    # 在本地，如果没有 .streamlit/secrets.toml，访问 st.secrets 会抛出 StreamlitSecretNotFoundError
    # 如果 st.secrets 可以访问，说明可能在 Streamlit Cloud 上或本地有 secrets.toml
    # 此时如果读取不到配置，应该通过 Secrets 配置而不是显示输入框
    try:
        # 尝试访问 st.secrets
        _ = st.secrets
        # 如果能访问（没有抛出 StreamlitSecretNotFoundError），认为可能在 Streamlit Cloud 上
        # 或者在本地有 secrets.toml，这两种情况都应该使用 Secrets 配置而不是输入框
        is_streamlit_cloud = True
    except StreamlitSecretNotFoundError:
        # 抛出 StreamlitSecretNotFoundError，确定在本地且没有 secrets.toml
        is_streamlit_cloud = False
    except (AttributeError, RuntimeError, Exception):
        # 其他异常，保守处理
        is_streamlit_cloud = False
    
    # 读取配置，按优先级：环境变量 > secrets > 配置文件 > session state
    # 先尝试从各个来源读取
    env_app_id = os.getenv("FEISHU_APP_ID")
    env_app_secret = os.getenv("FEISHU_APP_SECRET")
    secret_app_id = safe_get_secret("FEISHU_APP_ID")
    secret_app_secret = safe_get_secret("FEISHU_APP_SECRET")
    config_app_id = config.get("FEISHU_APP_ID")
    config_app_secret = config.get("FEISHU_APP_SECRET")
    session_app_id = st.session_state.get("feishu_app_id")
    session_app_secret = st.session_state.get("feishu_app_secret")
    
    app_id = env_app_id or secret_app_id or config_app_id or session_app_id
    app_secret = env_app_secret or secret_app_secret or config_app_secret or session_app_secret

    if not app_id or not app_secret:
        # 如果检测到在 Streamlit Cloud 上，显示配置提示而不是输入框
        if is_streamlit_cloud:
            # 提供更详细的诊断信息
            missing_items = []
            if not app_id:
                missing_items.append("FEISHU_APP_ID")
            if not app_secret:
                missing_items.append("FEISHU_APP_SECRET")
            
            error_msg = f"❌ 配置缺失：以下配置项未找到：{', '.join(missing_items)}\n\n"
            error_msg += "**请按以下步骤配置：**\n\n"
            error_msg += "1. 点击右上角 '⋮' → Settings → Secrets\n\n"
            error_msg += "2. 确保 Secrets 中包含以下配置（注意键名要完全匹配）：\n\n"
            error_msg += "```toml\n"
            error_msg += "[secrets]\n"
            error_msg += 'FEISHU_APP_ID = "cli_a9c84f993638dceb"\n'
            error_msg += 'FEISHU_APP_SECRET = "你的App_Secret"\n'
            error_msg += "```\n\n"
            error_msg += "3. **重要：** 点击 **Save changes** 按钮保存\n\n"
            error_msg += "4. 等待应用自动重新部署（通常需要 2-5 分钟）\n\n"
            error_msg += "5. 部署完成后，刷新此页面\n\n"
            error_msg += "⚠️ **如果已经配置并保存，但仍然显示此错误：**\n"
            error_msg += "- 确认 Secrets 格式正确（第一行是 `[secrets]`，使用英文双引号）\n"
            error_msg += "- 在 Secrets 末尾添加一个空行，再次点击 Save 以触发重新部署\n"
            error_msg += "- 等待至少 5 分钟后刷新页面\n\n"
            error_msg += "💡 App Secret 需要从[飞书开放平台](https://open.feishu.cn/)获取最新值。"
            
            st.error(error_msg)
            st.stop()
        else:
            # 本地环境，允许手动输入
            st.info(
                "请在下方输入 FEISHU_APP_ID 和 FEISHU_APP_SECRET，输入后会自动保存到本地配置文件，下次启动无需重新输入。"
                "注意：app_id/app_secret 与表格的 app_token/table_id 不同。"
            )
            app_id_input = st.text_input("FEISHU_APP_ID（飞书应用 App ID）", value=app_id or "")
            app_secret_input = st.text_input(
                "FEISHU_APP_SECRET（飞书应用 App Secret）", value=app_secret or "", type="password"
            )
            if not app_id_input or not app_secret_input:
                st.stop()
            # 保存到配置文件和 session state
            save_config(app_id_input, app_secret_input)
            st.session_state["feishu_app_id"] = app_id_input
            st.session_state["feishu_app_secret"] = app_secret_input
            app_id = app_id_input
            app_secret = app_secret_input
            st.success("✓ 凭据已保存，下次启动无需重新输入")
    else:
        # 如果已有凭据，显示已配置的提示
        source = "环境变量" if os.getenv("FEISHU_APP_ID") else ("secrets.toml" if safe_get_secret("FEISHU_APP_ID") else "本地配置文件")
        st.success(f"✓ 已检测到 FEISHU_APP_ID 和 FEISHU_APP_SECRET（来自 {source}）")

    # 大模型API配置（用于生成类似题目）
    st.markdown("---")
    st.markdown("### 大模型配置（用于生成类似题目）")
    llm_api_key = (
        os.getenv("LLM_API_KEY")
        or safe_get_secret("LLM_API_KEY")
        or config.get("LLM_API_KEY")
        or st.session_state.get("llm_api_key")
    )
    llm_api_base = (
        os.getenv("LLM_API_BASE")
        or safe_get_secret("LLM_API_BASE")
        or config.get("LLM_API_BASE")
        or st.session_state.get("llm_api_base")
        or None
    )
    llm_model = (
        os.getenv("LLM_MODEL")
        or safe_get_secret("LLM_MODEL")
        or config.get("LLM_MODEL")
        or st.session_state.get("llm_model")
        or None
    )
    
    # 如果没有配置API Base和Model，但有API Key，默认使用智谱GLM-4.6V
    if llm_api_key and not llm_api_base and not llm_model:
        llm_api_base = "https://open.bigmodel.cn/api/paas/v4"
        llm_model = "glm-4.6v"
        # 保存默认配置到session state，但不覆盖配置文件（用户可能需要手动配置）
        if "llm_api_base" not in st.session_state:
            st.session_state["llm_api_base"] = llm_api_base
        if "llm_model" not in st.session_state:
            st.session_state["llm_model"] = llm_model
    
    # 强制使用智谱AI的API Base URL（程序只支持智谱AI）
    if llm_api_key:
        llm_api_base = "https://open.bigmodel.cn/api/paas/v4"
        if "llm_api_base" not in st.session_state or st.session_state.get("llm_api_base") != llm_api_base:
            st.session_state["llm_api_base"] = llm_api_base
    
    if not llm_api_key:
        st.info("生成类似题目功能需要配置智谱AI API密钥。")
        
        # 直接使用智谱AI配置
        default_base = "https://open.bigmodel.cn/api/paas/v4"
        default_model = "glm-4.6v"
        help_text = "智谱AI API Base URL（使用 glm-4.6v，支持图片输入）"
        
        llm_api_key_input = st.text_input(
            "智谱AI API Key",
            value="",
            type="password",
            help="输入你的智谱AI API密钥"
        )
        # API Base URL固定为智谱AI，不允许修改
        st.text_input(
            "API Base URL",
            value=default_base,
            help=help_text,
            disabled=True
        )
        llm_api_base_input = default_base  # 强制使用智谱AI的API Base
        llm_model_input = st.text_input(
            "模型名称（可选，留空自动选择）",
            value=default_model,
            help="模型名称。推荐使用 glm-4.6v（支持图片输入）"
        )
        
        if llm_api_key_input:
            st.session_state["llm_api_key"] = llm_api_key_input
            st.session_state["llm_api_base"] = llm_api_base_input if llm_api_base_input else None
            st.session_state["llm_model"] = llm_model_input if llm_model_input else None
            # 保存到配置文件（在 Streamlit Cloud 上可能失败，这是正常的）
            try:
                config_file = get_config_file_path()
                if config_file.exists():
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                else:
                    config_data = {}
                config_data["LLM_API_KEY"] = llm_api_key_input
                if llm_api_base_input:
                    config_data["LLM_API_BASE"] = llm_api_base_input
                if llm_model_input:
                    config_data["LLM_MODEL"] = llm_model_input
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2)
            except (IOError, OSError, PermissionError):
                # 在 Streamlit Cloud 等只读文件系统上，保存失败是正常的
                pass
            except Exception:
                pass
            llm_api_key = llm_api_key_input
            llm_api_base = llm_api_base_input if llm_api_base_input else None
            llm_model = llm_model_input if llm_model_input else None
            st.success("✓ API配置已保存")
    else:
        st.success("✓ 已检测到 LLM_API_KEY")
        
        # 添加强制使用智谱AI的API Base URL（所有智谱AI模型都必须使用智谱AI API Base）
        llm_api_base = "https://open.bigmodel.cn/api/paas/v4"
        if "llm_api_base" not in st.session_state or st.session_state.get("llm_api_base") != llm_api_base:
            st.session_state["llm_api_base"] = llm_api_base
        
        # 显示修正后的API Base
        st.caption(f"API Base: {llm_api_base}")
        
        # 提供重新配置API Key的选项
        if st.checkbox("重新配置智谱AI API Key", key="reconfigure_api_key", help="如果API Key无效或已过期，可以勾选此选项重新输入"):
            st.info("💡 请输入新的智谱AI API Key。如果API Key无效，可以在[智谱AI开放平台](https://open.bigmodel.cn/)查看和更新。")
            new_api_key = st.text_input(
                "新的智谱AI API Key",
                value="",
                type="password",
                help="输入新的智谱AI API密钥",
                key="new_llm_api_key_input"
            )
            if new_api_key:
                st.session_state["llm_api_key"] = new_api_key
                # 保存到配置文件（在 Streamlit Cloud 上可能失败，这是正常的）
                try:
                    config_file = get_config_file_path()
                    if config_file.exists():
                        with open(config_file, "r", encoding="utf-8") as f:
                            config_data = json.load(f)
                    else:
                        config_data = {}
                    config_data["LLM_API_KEY"] = new_api_key
                    config_data["LLM_API_BASE"] = llm_api_base
                    if llm_model:
                        config_data["LLM_MODEL"] = llm_model
                    with open(config_file, "w", encoding="utf-8") as f:
                        json.dump(config_data, f, indent=2)
                    st.success("✓ 新的API Key已保存，请刷新页面或重新运行程序以生效")
                    st.session_state["reconfigure_api_key"] = False  # 取消勾选
                except (IOError, OSError, PermissionError):
                    # 在 Streamlit Cloud 上，配置文件是只读的，使用 session state 即可
                    st.info("💡 在 Streamlit Cloud 上，配置已保存到会话状态。建议通过 Secrets 配置环境变量以持久化。")
                    st.session_state["reconfigure_api_key"] = False
                except Exception:
                    st.warning("⚠️ 保存到配置文件失败，但已保存到会话状态。建议通过环境变量或 Secrets 配置。")
                    st.session_state["reconfigure_api_key"] = False
        
        # 保存原始配置的API Base，用于后续比较（但不再使用，只是为了兼容性保留变量）
        original_llm_api_base = llm_api_base
        
        # 智谱AI模型选项
        available_models = ["glm-4.6v", "glm-4", "glm-4-flash", "glm-3-turbo"]
        default_model_option = llm_model or "glm-4.6v"
        
        # 优先使用环境变量或配置中的模型，如果它在可用列表中
        # 如果环境变量中设置了模型，且该模型在可用列表中，使用环境变量中的
        preferred_model = None
        if llm_model and llm_model in available_models:
            preferred_model = llm_model
        else:
            preferred_model = default_model_option
        
        # 如果session state中没有保存的选择，或环境变量/配置中有模型，优先使用环境变量/配置中的
        if "selected_llm_model" not in st.session_state:
            st.session_state["selected_llm_model"] = preferred_model
        elif llm_model and llm_model in available_models:
            # 如果环境变量/配置中有模型，且与session state中的不同，更新为环境变量/配置中的
            st.session_state["selected_llm_model"] = llm_model
        
        # 确保session state中的模型在可用列表中，如果不在则重置为默认值
        current_selected = st.session_state.get("selected_llm_model")
        if current_selected not in available_models:
            st.session_state["selected_llm_model"] = preferred_model
            current_selected = preferred_model
        
        # 显示智谱AI模型选择器
        col_model1, col_model2 = st.columns([2, 3])
        with col_model1:
            selected_model = st.selectbox(
                "选择模型",
                options=available_models,
                index=available_models.index(current_selected) if current_selected in available_models else 0,
                help="可以在运行时切换不同的智谱AI模型，推荐使用 glm-4.6v（支持图片输入）",
                key="llm_model_selector"
            )
            # 更新session state
            st.session_state["selected_llm_model"] = selected_model
        
        with col_model2:
            if selected_model:
                # 检查模型是否来自环境变量
                model_source = ""
                if os.getenv("LLM_MODEL") == selected_model:
                    model_source = "（来自环境变量）"
                elif config.get("LLM_MODEL") == selected_model:
                    model_source = "（来自配置文件）"
                st.markdown(f"**当前模型**: {selected_model} {model_source}")
        
        # 使用选择的模型（优先使用用户选择的，其次使用配置的）
        llm_model = st.session_state.get("selected_llm_model") or llm_model
        
        # 确保API Base URL始终是智谱AI的（已经在上面修正过了，这里再次确认）
        llm_api_base = "https://open.bigmodel.cn/api/paas/v4"
        st.session_state["llm_api_base"] = llm_api_base

    try:
        token = get_tenant_access_token(app_id, app_secret)
        raw_records = fetch_records(token)
        records = parse_records(raw_records)
    except requests.exceptions.ConnectionError as exc:
        err_text = str(exc).lower()
        if "getaddrinfo" in err_text or "resolve" in err_text or "11001" in err_text:
            st.error(
                "**网络连接失败：无法解析 open.feishu.cn**\n\n"
                "本机无法解析飞书接口域名，多为 **DNS 或网络** 问题，请按顺序检查：\n\n"
                "1. **网络**：确认能正常上网，浏览器可打开 https://open.feishu.cn\n"
                "2. **DNS**：在 CMD 执行 `nslookup open.feishu.cn`，若失败可尝试：\n"
                "   - 改用 DNS：8.8.8.8 或 114.114.114.114\n"
                "   - 在「控制面板 → 网络和 Internet → 更改适配器选项」中编辑对应网卡，将 DNS 改为上述之一\n"
                "3. **代理/VPN**：若使用代理或 VPN，尝试关闭或切换节点后重试\n"
                "4. **公司网络**：若在公司内网，可能屏蔽了飞书，可换手机热点测试"
            )
        else:
            st.error("**连接飞书 API 失败**，请检查网络与防火墙：\n\n" + str(exc))
        return
    except RuntimeError as exc:
        msg = str(exc)
        if "99991663" in msg or "Invalid access token" in msg or "Invalid access token for authorization" in msg:
            st.error(
                "**飞书接口返回：访问令牌无效（99991663）**\n\n"
                "应用已成功获取 tenant_access_token，但调用多维表格时被拒绝，通常是因为 **应用未被加入该多维表格的协作者**。\n\n"
                "**若以前能正常用、近期没改过配置**：多半是飞书侧有变动——例如多维表格的 **协作者/分享被改**（应用被移出）、或飞书应用的 **权限/发布状态** 有更新。按下面步骤 **重新加一次协作者** 并检查开放平台，往往即可恢复。\n\n"
                "**请按以下步骤操作：**\n\n"
                "1. **把应用添加为多维表格协作者**\n"
                "   - 在飞书中打开该 **多维表格**（错题本所在的整个「多维表格」文档）\n"
                "   - 点击右上角 **「…」→「分享」** 或 **「协作」**\n"
                "   - 在协作者中添加 **你的应用（机器人）**，权限至少为 **「可阅读」**\n"
                "   - 若列表里找不到应用，先在 [飞书开放平台](https://open.feishu.cn) 找到该应用，在「权限管理」中开通 **多维表格 /  base:app** 等权限，并发布/启用\n\n"
                "2. **确认应用与多维表格匹配**\n"
                "   - 本程序用的 `app_token`（多维表格 ID）必须来自 **你已分享给该应用** 的多维表格\n"
                "   - 使用的 `FEISHU_APP_ID`、`FEISHU_APP_SECRET` 必须是该应用在开放平台的凭证\n\n"
                "3. **官方排查文档**\n"
                "   - [如何修复 99991663 错误](https://open.feishu.cn/document/uAjLw4CM/ugTN1YjL4UTN24CO1UjN/trouble-shooting/how-to-fix-99991663-error)"
            )
            return
        st.exception(exc)
        return
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)
        return

    if not records:
        st.warning("表格暂无记录，请先在飞书多维表格填充数据。")
        return

    # 学科多选
    subjects = sorted({r["subject"] for r in records if r.get("subject")})
    if not subjects:
        st.warning("记录里没有找到学科字段，请检查表头。")
        return

    selected_subjects = st.multiselect("选择学科（可多选）", options=subjects, default=subjects)
    if not selected_subjects:
        st.info("请选择至少一个学科。")
        st.stop()
    filtered = [r for r in records if r.get("subject") in selected_subjects]

    # 知识点多选
    knowledge_options = sorted(
        {kp for r in filtered for kp in r.get("knowledge_points") or []}
    )
    selected_kp = st.multiselect("选择知识点（可多选）", options=knowledge_options, default=knowledge_options)

    # 选择每个知识点的题目数量
    selected_plan: Dict[str, int] = {}
    for kp in selected_kp:
        pool = [r for r in filtered if kp in (r.get("knowledge_points") or [])]
        max_count = len(pool)
        default_count = max_count  # 默认最大
        count = st.number_input(
            f"{kp} 题目数量（最多 {max_count}）",
            min_value=0,
            max_value=max_count,
            step=1,
            value=default_count,
        )
        selected_plan[kp] = count

    # 检查是否有至少一个知识点选择了题目（数量 > 0）
    has_valid_selection = len(selected_plan) > 0 and any(count > 0 for count in selected_plan.values())
    
    if not has_valid_selection:
        if not selected_plan:
            st.info("⚠️ 请先选择知识点")
        else:
            st.info("⚠️ 请至少为一个知识点设置题目数量（大于0）才能生成题库")
    
    # 准备题目数据
    def prepare_selections():
        """准备选中的题目数据"""
        selections: Dict[str, List[Dict]] = {}
        for kp, count in selected_plan.items():
            if count <= 0:
                continue
            pool = [r for r in filtered if kp in (r.get("knowledge_points") or [])]
            if count > len(pool):
                count = len(pool)
            # 随机抽题
            if count > 0:
                selections[kp] = random.sample(pool, count)
        return selections
    
    def prepare_similar_selections(llm_api_key: str, llm_api_base: str = None, llm_model: str = None, token: str = None):
        """
        准备类似题目数据：取前 X 道（X=用户选择的数量）最近创建的题目作为参考，每道参考题生成 1 道类似题。
        
        Args:
            llm_api_key: 大模型API密钥
            llm_api_base: 大模型API基础URL（可选）
            llm_model: 模型名称（可选）
            token: 飞书访问token，用于下载图片附件（可选）
        """
        similar_selections: Dict[str, List[Dict]] = {}
        total_upper = sum(c for c in selected_plan.values() if c > 0)
        progress_bar = st.progress(0.0) if total_upper > 0 else None
        current = 0
        
        for kp, count in selected_plan.items():
            if count <= 0:
                continue
            
            # 获取该知识点的所有题目
            pool = [r for r in filtered if kp in (r.get("knowledge_points") or [])]
            if not pool:
                continue
            
            # 仅保留有「去手写」或附件的题目
            pool_with_time = [
                (r, r.get("created_time", 0))
                for r in pool
                if r.get("handwriting_text") or r.get("attachments")
            ]
            
            if not pool_with_time:
                continue
            
            # 按创建时间降序排序（最近的在前面），取前 X 道（X=用户选择的数量）作为参考题
            pool_with_time.sort(key=lambda x: x[1], reverse=True)
            X = min(count, len(pool_with_time))
            reference_questions = [pool_with_time[i][0] for i in range(X)]
            
            # 对每道参考题生成 1 道类似题
            generated_questions = []
            for ref in reference_questions:
                try:
                    texts = generate_similar_questions_with_llm(ref, 1, llm_api_key, llm_api_base, llm_model, token)
                    if texts:
                        generated_questions.append({
                            "subject": ref.get("subject"),
                            "knowledge_points": [kp],
                            "handwriting_text": texts[0],
                            "reason_type": "",
                            "reason_detail": "",
                            "attachments": [],
                            "created_time": 0,
                        })
                except Exception as e:
                    st.error(f"知识点 {kp} 生成类似题目失败：{str(e)}")
                    # 该参考题失败后继续处理下一道，不中断整个知识点
                current += 1
                if progress_bar:
                    progress_bar.progress(min(1.0, current / total_upper))
            
            if generated_questions:
                similar_selections[kp] = generated_questions
        
        if progress_bar:
            progress_bar.progress(1.0)
        return similar_selections
    
    # 使用两列布局放置按钮
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("生成题库WORD文档", type="primary", disabled=not has_valid_selection, use_container_width=True):
            with st.spinner("正在生成题库WORD文档，请稍候..."):
                try:
                    selections = prepare_selections()

                    if not selections or sum(len(v) for v in selections.values()) == 0:
                        st.warning("当前选择下没有可用题目。")
                        return

                    doc_bytes = build_doc(selected_subjects, selections, token)
                    filename = f"{'、'.join(selected_subjects)}_错题专项训练.docx"
                    st.success("✓ 题库WORD文档已生成，可以下载。")
                    st.download_button(
                        "📥 下载 Word 文档",
                        data=doc_bytes,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"生成题库WORD文档时出错：{exc}")
                    st.exception(exc)
    
    with col2:
        if st.button("生成题库HTML", type="primary", disabled=not has_valid_selection, use_container_width=True):
            with st.spinner("正在生成题库HTML，请稍候..."):
                try:
                    selections = prepare_selections()

                    if not selections or sum(len(v) for v in selections.values()) == 0:
                        st.warning("当前选择下没有可用题目。")
                        return

                    html_content = build_html(selected_subjects, selections, token)
                    filename = f"{'、'.join(selected_subjects)}_错题专项训练.html"
                    st.success("✓ 题库HTML已生成，可以下载。")
                    st.download_button(
                        "📥 下载 HTML 文档",
                        data=html_content.encode('utf-8'),
                        file_name=filename,
                        mime="text/html",
                        use_container_width=True,
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"生成题库HTML时出错：{exc}")
                    st.exception(exc)
    
    # 添加类似题目按钮（使用新的两列布局）
    st.markdown("---")  # 分隔线
    st.markdown("### 生成类似题目")
    if not llm_api_key:
        st.warning("⚠️ 生成类似题目功能需要配置智谱AI API密钥，请在上方配置区域输入。")
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("生成类似题目WORD文档", type="primary", disabled=not has_valid_selection or not llm_api_key, use_container_width=True):
            if not llm_api_key:
                st.error("请先配置大模型API密钥才能生成类似题目")
                return
            with st.spinner("正在使用大模型生成类似题目，请稍候..."):
                try:
                    similar_selections = prepare_similar_selections(llm_api_key, llm_api_base, llm_model, token)

                    if not similar_selections or sum(len(v) for v in similar_selections.values()) == 0:
                        st.warning("生成类似题目失败或没有可用题目。")
                        return

                    doc_bytes = build_doc(selected_subjects, similar_selections, token)
                    filename = f"{'、'.join(selected_subjects)}_类似题目专项训练.docx"
                    st.success("✓ 类似题目WORD文档已生成，可以下载。")
                    st.download_button(
                        "📥 下载 Word 文档",
                        data=doc_bytes,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except Exception as exc:  # noqa: BLE001
                    error_msg = str(exc)
                    st.error(f"生成类似题目WORD文档时出错：{error_msg}")
                    
                    # 检查是否是API认证相关的错误
                    if any(keyword in error_msg.lower() for keyword in ["401", "unauthorized", "authentication", "api key", "invalid", "forbidden", "403", "令牌已过期", "验证不正确"]):
                        st.error("""
                        ⚠️ **API认证失败（401错误）**
                        
                        **可能的原因：**
                        1. 智谱AI API Key不正确或已过期
                        2. API Key没有足够的权限
                        3. API Key与当前使用的模型不匹配
                        
                        **解决方法：**
                        1. 请前往[智谱AI开放平台](https://open.bigmodel.cn/)检查并更新API Key
                        2. 在上方"大模型配置"区域重新输入正确的API Key
                        3. 确认API Key有权限使用glm-4.6v或glm-4模型
                        """)
                    else:
                        st.exception(exc)
    
    with col4:
        if st.button("生成类似题目HTML", type="primary", disabled=not has_valid_selection or not llm_api_key, use_container_width=True):
            if not llm_api_key:
                st.error("请先配置大模型API密钥才能生成类似题目")
                return
            with st.spinner("正在使用大模型生成类似题目，请稍候..."):
                try:
                    similar_selections = prepare_similar_selections(llm_api_key, llm_api_base, llm_model, token)

                    if not similar_selections or sum(len(v) for v in similar_selections.values()) == 0:
                        st.warning("生成类似题目失败或没有可用题目。")
                        return

                    html_content = build_html(selected_subjects, similar_selections, token)
                    filename = f"{'、'.join(selected_subjects)}_类似题目专项训练.html"
                    st.success("✓ 类似题目HTML已生成，可以下载。")
                    st.download_button(
                        "📥 下载 HTML 文档",
                        data=html_content.encode('utf-8'),
                        file_name=filename,
                        mime="text/html",
                        use_container_width=True,
                    )
                except Exception as exc:  # noqa: BLE001
                    error_msg = str(exc)
                    st.error(f"生成类似题目HTML时出错：{error_msg}")
                    
                    # 检查是否是API认证相关的错误
                    if any(keyword in error_msg.lower() for keyword in ["401", "unauthorized", "authentication", "api key", "invalid", "forbidden", "403", "令牌已过期", "验证不正确"]):
                        st.error("""
                        ⚠️ **API认证失败（401错误）**
                        
                        **可能的原因：**
                        1. 智谱AI API Key不正确或已过期
                        2. API Key没有足够的权限
                        3. API Key与当前使用的模型不匹配
                        
                        **解决方法：**
                        1. 请前往[智谱AI开放平台](https://open.bigmodel.cn/)检查并更新API Key
                        2. 在上方"大模型配置"区域重新输入正确的API Key
                        3. 确认API Key有权限使用glm-4.6v或glm-4模型
                        """)
                    else:
                        st.exception(exc)

    # ----- 错题练习 -----
    st.markdown("---")
    st.markdown("### 错题练习")
    practice_table_id = (
        os.getenv("FEISHU_PRACTICE_TABLE_ID")
        or safe_get_secret("FEISHU_PRACTICE_TABLE_ID")
        or config.get("FEISHU_PRACTICE_TABLE_ID")
        or ""
    )
    filtered_practice = (
        filtered
        if not selected_kp
        else [r for r in filtered if any(kp in (r.get("knowledge_points") or []) for kp in selected_kp)]
    )

    def _go_next_practice() -> None:
        pm = st.session_state.get("practice_map", {})
        pf = st.session_state.get("practice_filtered", [])
        n = pick_next_question(pf, pm, int(time.time() * 1000))
        if n:
            st.session_state["practice_current"] = n
            st.session_state["practice_origin"] = None
            st.session_state["practice_is_similar"] = False
            st.session_state["practice_similar_count"] = 0
        else:
            for k in ("practice_current", "practice_origin", "practice_is_similar", "practice_similar_count"):
                st.session_state.pop(k, None)
            st.success("本轮可复习的题目已练完。")

    if st.session_state.get("practice_current"):
        cur = st.session_state["practice_current"]
        st.session_state.setdefault("practice_map", {})
        st.session_state.setdefault("practice_filtered", [])
        if st.session_state.get("practice_is_similar"):
            st.caption("类似题")
        render_question_streamlit(cur, token)
        st.caption("掌握了吗？")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("会", key="practice_btn_yes"):
                is_sim = st.session_state.get("practice_is_similar", False)
                if not is_sim:
                    save_practice_feedback(
                        token,
                        st.session_state["practice_table_id"],
                        (cur.get("record_id") or "").strip(),
                        True,
                        st.session_state["practice_map"],
                    )
                _go_next_practice()
                st.rerun()
        with col_b:
            if st.button("不会", key="practice_btn_no"):
                is_sim = st.session_state.get("practice_is_similar", False)
                orig = st.session_state.get("practice_origin")
                ptid = st.session_state.get("practice_table_id", "")
                pm = st.session_state.get("practice_map", {})
                if not is_sim:
                    save_practice_feedback(
                        token,
                        ptid,
                        (cur.get("record_id") or "").strip(),
                        False,
                        pm,
                    )
                    st.session_state["practice_origin"] = cur
                    if llm_api_key:
                        with st.spinner("正在生成类似题目…"):
                            try:
                                texts = generate_similar_questions_with_llm(
                                    cur, 1, llm_api_key, llm_api_base, llm_model, token
                                )
                                if texts:
                                    st.session_state["practice_current"] = {
                                        "handwriting_text": texts[0],
                                        "attachments": [],
                                        "record_id": "",
                                    }
                                    st.session_state["practice_is_similar"] = True
                                    st.session_state["practice_similar_count"] = 1
                                    st.rerun()
                                else:
                                    _go_next_practice()
                            except Exception as e:
                                st.error(f"生成类似题目失败：{e}，跳过类似题进入下一道")
                                _go_next_practice()
                    else:
                        st.warning("未配置智谱AI API Key，无法生成类似题，直接进入下一道")
                        _go_next_practice()
                else:
                    cnt = st.session_state.get("practice_similar_count", 0)
                    if cnt < 2 and llm_api_key and orig:
                        with st.spinner("再出一道类似题目…"):
                            try:
                                texts = generate_similar_questions_with_llm(
                                    orig, 1, llm_api_key, llm_api_base, llm_model, token
                                )
                                if texts:
                                    st.session_state["practice_current"] = {
                                        "handwriting_text": texts[0],
                                        "attachments": [],
                                        "record_id": "",
                                    }
                                    st.session_state["practice_similar_count"] = 2
                                    st.rerun()
                                else:
                                    _go_next_practice()
                            except Exception:
                                _go_next_practice()
                    else:
                        _go_next_practice()
                st.rerun()
    else:
        if not practice_table_id:
            st.error(
                "错题练习需要配置 **FEISHU_PRACTICE_TABLE_ID**（练习记录表的 table_id）。"
                "请在环境变量、Secrets 或 `.feishu_config.json` 中配置。"
                "需在同一多维表格下新建一张表，包含字段：错题record_id、上次练习时间、掌握程度、练习次数、下次练习时间。"
            )
        else:
            if st.button("开始练习", key="practice_start"):
                with st.spinner("正在加载练习记录…"):
                    try:
                        pm = fetch_practice_records(token, practice_table_id)
                        n = pick_next_question(filtered_practice, pm, int(time.time() * 1000))
                        if not n:
                            st.info("暂无需要复习的题目，或在本筛选条件下可复习的题目已练完。")
                        else:
                            st.session_state["practice_current"] = n
                            st.session_state["practice_map"] = pm
                            st.session_state["practice_table_id"] = practice_table_id
                            st.session_state["practice_filtered"] = filtered_practice
                            st.session_state["practice_origin"] = None
                            st.session_state["practice_is_similar"] = False
                            st.session_state["practice_similar_count"] = 0
                            st.rerun()
                    except Exception as e:
                        st.error(f"加载练习记录失败：{e}")


if __name__ == "__main__":
    main()
