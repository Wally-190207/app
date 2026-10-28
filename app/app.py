import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime

# ==========================================
# 0. BOOTSTRAPPER: TỰ ĐỘNG CÀI ĐẶT STREAMLIT & KHỞI CHẠY SERVER
# ==========================================
def _ensure_streamlit_installed() -> None:
    """
    Kiểm tra và tự động cài đặt thư viện streamlit vào đúng Python Interpreter (sys.executable)
    đang chạy (khắc phục triệt để lỗi ModuleNotFoundError trong Visual Studio / VS Code).
    """
    try:
        import streamlit  # noqa: F401
    except ModuleNotFoundError:
        print("⚠️ Phát hiện môi trường Python hiện tại chưa có thư viện 'streamlit'.")
        print(f"🔧 Đang tự động cài đặt 'streamlit' vào: {sys.executable} ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        except Exception:
            try:
                import ensurepip
                ensurepip.bootstrap()
            except Exception:
                pass
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("✅ Đã cài đặt 'streamlit' thành công!")


_ensure_streamlit_installed()

import streamlit as st  # noqa: E402
import streamlit.components.v1 as components  # noqa: E402

# Tự động khởi chạy Streamlit Server nếu người dùng nhấn nút Run (python app.py) trực tiếp trong VS / VS Code
if __name__ == "__main__":
    try:
        is_running_in_streamlit = st.runtime.exists()
    except Exception:
        is_running_in_streamlit = False

    if not is_running_in_streamlit:
        script_path = os.path.abspath(__file__)
        os.chdir(os.path.dirname(script_path))
        print("🚀 Đang khởi động Streamlit Web Server... Vui lòng mở link Local URL bên dưới:")
        sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", script_path]))

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN CÔNG NGHỆ (TECH UI)
# ==========================================
st.set_page_config(
    page_title="Model ĐĐT - Kỹ thuật Điện - Điện tử",
    page_icon="⚡",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")


def inject_tech_background_css() -> None:
    """
    Tiêm CSS tạo nền tảng Công nghệ Kỹ thuật Điện - Điện tử (PCB Circuit Grid + Glowing Nodes + Glassmorphism Cards)
    giúp không gian trực quan, hiện đại và đỡ trống trải.
    """
    st.markdown(
        """
        <style>
        /* Nền chính kiểu bản mạch điện tử (Circuit Board Grid) kết hợp ánh sáng công nghệ */
        .stApp {
            background-color: #070d19;
            background-image:
                radial-gradient(circle at 12% 18%, rgba(14, 165, 233, 0.16) 0%, transparent 32%),
                radial-gradient(circle at 88% 82%, rgba(59, 130, 246, 0.15) 0%, transparent 35%),
                radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.06) 0%, transparent 45%),
                linear-gradient(rgba(56, 189, 248, 0.06) 1px, transparent 1px),
                linear-gradient(90deg, rgba(56, 189, 248, 0.06) 1px, transparent 1px),
                linear-gradient(rgba(56, 189, 248, 0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(56, 189, 248, 0.025) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 100% 100%, 100px 100px, 100px 100px, 20px 20px, 20px 20px;
            background-position: 0 0, 0 0, 0 0, -1px -1px, -1px -1px, -1px -1px, -1px -1px;
            background-attachment: fixed;
            color: #e2e8f0;
        }

        /* Thanh Sidebar phong cách bảng điều khiển kỹ thuật */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10, 18, 36, 0.96) 0%, rgba(15, 23, 42, 0.96) 100%) !important;
            border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
            box-shadow: 4px 0 24px rgba(2, 132, 199, 0.12);
        }

        /* Khung thẻ (Container border=True) hiệu ứng kính mờ công nghệ (Tech Glassmorphism) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(15, 23, 42, 0.78) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(56, 189, 248, 0.28) !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35), inset 0 0 18px rgba(56, 189, 248, 0.04) !important;
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(56, 189, 248, 0.55) !important;
            box-shadow: 0 10px 32px rgba(2, 132, 199, 0.22), inset 0 0 22px rgba(56, 189, 248, 0.07) !important;
        }

        /* Tiêu đề & chữ hiển thị sắc nét trên nền tối công nghệ */
        h1, h2, h3, h4, h5, h6 {
            color: #f8fafc !important;
            letter-spacing: 0.2px;
        }
        p, li, label, .stMarkdown {
            color: #e2e8f0 !important;
        }
        [data-testid="stCaptionContainer"] p {
            color: #94a3b8 !important;
        }

        /* Nút bấm Primary mang sắc xanh điện tử (Electric Cyan-Blue) */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(125, 211, 252, 0.4) !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
            border-color: #7dd3fc !important;
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.5);
            transform: translateY(-1px);
        }

        /* Nút bấm Secondary */
        .stButton > button[kind="secondary"] {
            background: rgba(30, 41, 59, 0.85) !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(148, 163, 184, 0.35) !important;
        }
        .stButton > button[kind="secondary"]:hover {
            border-color: #38bdf8 !important;
            color: #38bdf8 !important;
            background: rgba(15, 23, 42, 0.95) !important;
        }

        /* Dialog Modal công nghệ */
        div[role="dialog"] {
            background: #0f172a !important;
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.75), 0 0 30px rgba(14, 165, 233, 0.2) !important;
            border-radius: 14px !important;
        }

        /* Thẻ code inline nổi bật */
        code {
            background: rgba(14, 165, 233, 0.15) !important;
            color: #38bdf8 !important;
            border: 1px solid rgba(56, 189, 248, 0.25);
            padding: 2px 6px !important;
            border-radius: 5px !important;
        }

        /* Banner trang trí mạch điện trên đầu trang */
        .tech-hero-banner {
            background: linear-gradient(90deg, rgba(14, 165, 233, 0.14) 0%, rgba(37, 99, 235, 0.08) 50%, rgba(16, 185, 129, 0.1) 100%);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-left: 4px solid #38bdf8;
            border-radius: 10px;
            padding: 14px 20px;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .tech-badge {
            display: inline-block;
            background: rgba(14, 165, 233, 0.2);
            border: 1px solid rgba(56, 189, 248, 0.45);
            color: #7dd3fc;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 999px;
            letter-spacing: 0.5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


inject_tech_background_css()

# ==========================================
# 2. QUẢN LÝ DỮ LIỆU, LƯU TRỮ & ĐỒNG BỘ GITHUB CLOUD (DATA LAYER)
# ==========================================
DEFAULT_DATA = [
    {
        "id": "model-hinh-1-1",
        "title": "Hình 1.1: Mô hình mạch điện",
        "category": "1.1. Các khái niệm cơ bản trong mạch điện - 1.1.1. Mô hình mạch điện",
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "symbol": "H1.1",
        "diagram_type": "fig_1_1",
        "diagram_image": "",
        "hotspots": [],
        "concept": (
            "Mạch điện là tập hợp các thiết bị điện nối với nhau bằng các dây dẫn tạo thành những mạch kín "
            "trong đó dòng điện có thể chạy qua. Mạch điện thường gồm các phần tử: nguồn điện, phụ tải (tải), "
            "dây dẫn. Ngoài ra còn có các thiết bị phụ trợ để bảo vệ và điều khiển như cầu dao, áp tô mát, cầu chì, rơle..."
        ),
        "devices": [
            {
                "device_id": "h11-nguon",
                "symbol": "Nguồn",
                "name": "Nguồn điện",
                "concept": (
                    "Nguồn điện là thiết bị điện tạo ra điện năng. Về nguyên lý, nguồn điện là thiết bị biến đổi "
                    "các dạng năng lượng như cơ năng, hóa năng, nhiệt năng, năng lượng bức xạ mặt trời, v.v... thành điện năng."
                ),
                "details": (
                    "Ví dụ thực tế trong kỹ thuật:\n"
                    "- Pin, ắc quy: Biến đổi hóa năng thành điện năng.\n"
                    "- Máy phát điện: Biến đổi cơ năng thành điện năng.\n"
                    "- Pin mặt trời: Biến đổi năng lượng bức xạ mặt trời thành điện năng."
                ),
                "real_images": []
            },
            {
                "device_id": "h11-tai",
                "symbol": "Tải",
                "name": "Phụ tải (Tải)",
                "concept": (
                    "Tải là các thiết bị tiêu thụ điện năng và biến đổi điện năng thành các dạng năng lượng khác "
                    "như cơ năng, nhiệt năng, quang năng, v.v..."
                ),
                "details": (
                    "Ví dụ thực tế trong kỹ thuật:\n"
                    "- Động cơ điện: Tiêu thụ điện năng và biến điện năng thành cơ năng.\n"
                    "- Bàn là, bếp điện: Biến điện năng thành nhiệt năng.\n"
                    "- Bóng đèn: Biến điện năng thành quang năng."
                ),
                "real_images": []
            },
            {
                "device_id": "h11-daydan",
                "symbol": "Dây dẫn",
                "name": "Dây dẫn",
                "concept": "Dây dẫn dùng để dẫn điện từ nguồn đến phụ tải, nối các thiết bị điện tạo thành mạch kín.",
                "details": (
                    "Ngoài nguồn điện, phụ tải và dây dẫn, trên đường dây mạch điện còn lắp đặt các thiết bị phụ trợ "
                    "để bảo vệ và điều khiển như: cầu dao, áp tô mát, cầu chì, rơle..."
                ),
                "real_images": []
            }
        ]
    },
    {
        "id": "model-hinh-1-2",
        "title": "Hình 1.2: Kết cấu hình học của mạch điện",
        "category": "1.1. Các khái niệm cơ bản trong mạch điện - 1.1.2. Kết cấu hình học của mạch điện",
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "symbol": "H1.2",
        "diagram_type": "fig_1_2",
        "diagram_image": "",
        "hotspots": [],
        "concept": (
            "Kết cấu hình học của mạch điện được mô tả thông qua các phần tử cơ bản (Nguồn, Tải, Dây dẫn) "
            "và các khái niệm hình học của mạch gồm: Nhánh, Nút và Vòng (mạch vòng)."
        ),
        "devices": [
            {
                "device_id": "h12-nguon",
                "symbol": "E1, E2",
                "name": "Nguồn điện (E1, E2)",
                "concept": (
                    "Nguồn điện trong sơ đồ Hình 1.2 gồm hai nguồn sức điện động E1 và E2 cung cấp điện năng cho mạch."
                ),
                "details": (
                    "- Nguồn E1: Nằm trên nhánh 1 (phía bên trái), nối tiếp với điện trở R1.\n"
                    "- Nguồn E2: Nằm trên nhánh 2 (phía bên phải), nối tiếp với điện trở R2.\n"
                    "- Ký hiệu: Hình tròn có mũi tên chỉ chiều sức điện động ở bên trong."
                ),
                "real_images": []
            },
            {
                "device_id": "h12-tai",
                "symbol": "R1, R2, R3",
                "name": "Phụ tải / Điện trở (R1, R2, R3)",
                "concept": (
                    "Các phần tử tiêu thụ điện năng đặc trưng bởi các điện trở R1, R2, R3 phân bố trên 3 nhánh của mạch điện."
                ),
                "details": (
                    "- Điện trở R1: Thuộc nhánh 1, có dòng điện I1 chạy qua.\n"
                    "- Điện trở R2: Thuộc nhánh 2, có dòng điện I2 chạy qua.\n"
                    "- Điện trở R3: Thuộc nhánh 3 (nhánh giữa nối giữa hai nút A và B), có dòng điện I3 chạy qua."
                ),
                "real_images": []
            },
            {
                "device_id": "h12-daydan",
                "symbol": "Dây dẫn",
                "name": "Dây dẫn nối mạch",
                "concept": "Dây dẫn dùng để dẫn điện và liên kết các phần tử E1, E2, R1, R2, R3 tạo thành các nhánh và mạch vòng khép kín.",
                "details": "Trên sơ đồ kỹ thuật, dây dẫn được biểu diễn bằng các đoạn thẳng nối liền giữa các phần tử và giao nhau tại các nút A, B.",
                "real_images": []
            },
            {
                "device_id": "h12-nhanh",
                "symbol": "Nhánh (I1, I2, I3)",
                "name": "Nhánh mạch điện",
                "concept": (
                    "Nhánh là 1 đoạn mạch gồm những phần tử ghép nối tiếp nhau, trong đó có cùng 1 dòng điện "
                    "chạy thông từ đầu nọ đến đầu kia."
                ),
                "details": (
                    "Trong Hình 1.2 bao gồm 3 nhánh:\n"
                    "- Nhánh 1: Gồm nguồn E1 và điện trở R1 (có dòng điện I1 chạy qua).\n"
                    "- Nhánh 2: Gồm nguồn E2 và điện trở R2 (có dòng điện I2 chạy qua).\n"
                    "- Nhánh 3: Gồm điện trở R3 nối giữa nút A và nút B (có dòng điện I3 chạy qua)."
                ),
                "real_images": []
            },
            {
                "device_id": "h12-nut",
                "symbol": "Nút A, Nút B",
                "name": "Nút mạch điện",
                "concept": "Nút là giao điểm gặp nhau của 3 nhánh trở lên.",
                "details": (
                    "Trong Hình 1.2 bao gồm 2 nút (ký hiệu bằng chấm tròn đen tại điểm giao của 3 nhánh):\n"
                    "- Nút A: Điểm giao nhau phía trên của 3 nhánh (Nhánh 1, Nhánh 2, Nhánh 3).\n"
                    "- Nút B: Điểm giao nhau phía dưới của 3 nhánh (Nhánh 1, Nhánh 2, Nhánh 3)."
                ),
                "real_images": []
            },
            {
                "device_id": "h12-vong",
                "symbol": "",
                "name": "Vòng (mạch vòng)",
                "concept": (
                    "Mạch vòng là một đường dẫn khép kín mà nó bắt đầu và kết thúc ở cùng một điểm "
                    "đi qua các phần tử của mạch điện. (Khái niệm này không có ký hiệu riêng trên hình)."
                ),
                "details": (
                    "Trong Hình 1.2 bao gồm 3 vòng:\n"
                    "- Vòng 1: Bao gồm các phần tử: Nguồn E1, điện trở R1, điện trở R3.\n"
                    "- Vòng 2: Bao gồm điện trở R2, nguồn E2 và điện trở R3.\n"
                    "- Vòng 3: Bao gồm nguồn E1, điện trở R1, điện trở R2 và nguồn E2."
                ),
                "real_images": []
            }
        ]
    }
]


def get_github_config() -> dict:
    """
    Lấy cấu hình kết nối GitHub API từ session_state (nếu nhập trực tiếp), st.secrets (trên Streamlit Cloud)
    hoặc biến môi trường (os.environ).
    """
    token = ""
    repo = ""
    branch = "main"
    file_path = "data.json"

    # 1. Đọc từ st.secrets (Streamlit Cloud)
    try:
        if "GITHUB_TOKEN" in st.secrets:
            token = str(st.secrets["GITHUB_TOKEN"]).strip()
        if "GITHUB_REPO" in st.secrets:
            repo = str(st.secrets["GITHUB_REPO"]).strip()
        if "GITHUB_BRANCH" in st.secrets:
            branch = str(st.secrets["GITHUB_BRANCH"]).strip() or "main"
        if "GITHUB_FILE_PATH" in st.secrets:
            file_path = str(st.secrets["GITHUB_FILE_PATH"]).strip() or "data.json"
    except Exception:
        pass

    # 2. Dự phòng đọc từ biến môi trường hệ thống
    if not token:
        token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not repo:
        repo = os.environ.get("GITHUB_REPO", "").strip()
    if os.environ.get("GITHUB_BRANCH"):
        branch = os.environ.get("GITHUB_BRANCH", "main").strip()

    # 3. Ưu tiên cấu hình tạm thời nếu người dùng nhập trực tiếp trên Sidebar
    if "custom_github_config" in st.session_state:
        custom_cfg = st.session_state.custom_github_config
        if custom_cfg.get("token") and custom_cfg.get("repo"):
            token = custom_cfg["token"].strip()
            repo = custom_cfg["repo"].strip()
            branch = custom_cfg.get("branch", "main").strip() or "main"

    # Chuẩn hóa định dạng repo (loại bỏ https://github.com/ nếu người dùng dán nguyên link)
    repo = repo.replace("https://github.com/", "").replace("http://github.com/", "").strip("/")
    if repo.endswith(".git"):
        repo = repo[:-4]

    return {
        "token": token,
        "repo": repo,
        "branch": branch,
        "path": file_path,
        "enabled": bool(token and repo and "/" in repo)
    }


def github_pull_data() -> list | None:
    """Tải nội dung file data.json trực tiếp từ kho chứa GitHub thông qua GitHub REST API."""
    cfg = get_github_config()
    if not cfg["enabled"]:
        return None

    api_url = (
        f"https://api.github.com/repos/{cfg['repo']}/contents/{cfg['path']}"
        f"?ref={urllib.parse.quote(cfg['branch'])}"
    )
    req = urllib.request.Request(
        api_url,
        headers={
            "Authorization": f"Bearer {cfg['token']}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Model-DDT-Streamlit-App"
        },
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_json = json.loads(resp.read().decode("utf-8"))
            content_b64 = resp_json.get("content", "")
            if content_b64:
                decoded_str = base64.b64decode(content_b64).decode("utf-8")
                return json.loads(decoded_str)
    except Exception:
        return None
    return None


def github_push_data(data: list, commit_msg: str = "Auto-sync data.json from Model DDT Web App") -> tuple[bool, str]:
    """Đẩy (Commit & Push) toàn bộ dữ liệu data.json mới nhất thẳng lên GitHub thông qua GitHub REST API."""
    cfg = get_github_config()
    if not cfg["enabled"]:
        return False, "Chưa cấu hình GitHub Token/Repo."

    base_url = f"https://api.github.com/repos/{cfg['repo']}/contents/{cfg['path']}"
    headers = {
        "Authorization": f"Bearer {cfg['token']}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "Model-DDT-Streamlit-App"
    }

    # Bước 1: Lấy mã SHA hiện tại của file data.json trên nhánh GitHub (nếu file đã tồn tại)
    current_sha = None
    get_url = f"{base_url}?ref={urllib.parse.quote(cfg['branch'])}"
    get_req = urllib.request.Request(get_url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(get_req, timeout=10) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
            current_sha = meta.get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return False, f"Lỗi kiểm tra file trên GitHub (HTTP {e.code})."
    except Exception as e:
        return False, f"Lỗi kết nối GitHub: {e}"

    # Bước 2: Mã hóa Base64 và gửi lệnh PUT để cập nhật file trên GitHub
    raw_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    b64_content = base64.b64encode(raw_bytes).decode("utf-8")

    payload = {
        "message": commit_msg,
        "content": b64_content,
        "branch": cfg["branch"]
    }
    if current_sha:
        payload["sha"] = current_sha

    put_req = urllib.request.Request(
        base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="PUT"
    )
    try:
        with urllib.request.urlopen(put_req, timeout=15) as resp:
            if resp.status in (200, 201):
                return True, ""
            return False, f"GitHub trả về mã trạng thái: {resp.status}"
    except urllib.error.HTTPError as e:
        try:
            err_detail = json.loads(e.read().decode("utf-8")).get("message", "")
        except Exception:
            err_detail = str(e)
        return False, f"Lỗi ghi GitHub (HTTP {e.code}): {err_detail}"
    except Exception as e:
        return False, f"Không thể đồng bộ lên GitHub: {e}"


def _normalize_loaded_models(data: list) -> list:
    """Đảm bảo mọi mô hình và thiết bị đều có đủ các trường tương thích (diagram_image, hotspots, real_images)."""
    for model in data:
        if "diagram_image" not in model or not isinstance(model["diagram_image"], str):
            model["diagram_image"] = ""
        if "hotspots" not in model or not isinstance(model["hotspots"], list):
            model["hotspots"] = []
        for dev in model.get("devices", []):
            if "real_images" not in dev or not isinstance(dev["real_images"], list):
                dev["real_images"] = []
    return data


def load_data() -> list:
    """
    Đọc dữ liệu từ GitHub (nếu đã cấu hình Auto-Sync) hoặc từ file data.json nội bộ.
    Đảm bảo tương thích trường real_images, diagram_image và hotspots.
    """
    # 1. Ưu tiên kéo dữ liệu mới nhất từ GitHub nếu đã cấu hình
    remote_data = github_pull_data()
    if isinstance(remote_data, list) and remote_data:
        normalized_remote = _normalize_loaded_models(remote_data)
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(normalized_remote, f, ensure_ascii=False, indent=2)
        except IOError:
            pass
        return normalized_remote

    # 2. Đọc từ file data.json nội bộ nếu chưa cấu hình GitHub hoặc kho chưa có file
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        old_symbols = {"DOL-3P", "AC-DC-7812"}
        if data and all(item.get("symbol") in old_symbols for item in data):
            save_data(DEFAULT_DATA)
            return DEFAULT_DATA
        return _normalize_loaded_models(data)
    except (json.JSONDecodeError, IOError):
        return []


def save_data(data: list) -> None:
    """
    Ghi đè dữ liệu bền vững xuống file data.json nội bộ, đồng thời tự động đồng bộ (Push)
    lên GitHub Repository nếu đã cấu hình GitHub Auto-Sync.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError:
        pass

    cfg = get_github_config()
    if cfg["enabled"]:
        ok, err_msg = github_push_data(data)
        if not ok:
            st.warning(f"⚠️ Đã lưu tạm thời nhưng chưa thể đồng bộ lên GitHub: {err_msg}")


def init_session_state() -> None:
    """Khởi tạo st.session_state để quản lý trạng thái tức thời."""
    if "models_data" not in st.session_state:
        st.session_state.models_data = load_data()
    if "current_view" not in st.session_state:
        st.session_state.current_view = "main"
    if "selected_model_id" not in st.session_state:
        st.session_state.selected_model_id = None
    if "selected_device" not in st.session_state:
        st.session_state.selected_device = None


init_session_state()


def navigate_to_device_detail(model_id: str, dev: dict) -> None:
    """
    Callback xử lý chuyển sang trang chi tiết thiết bị ngay khi người dùng
    nhấn vào ký hiệu thiết bị (trên bản vẽ SVG, ảnh sơ đồ tùy chỉnh hoặc nút ký hiệu).
    """
    st.session_state.selected_model_id = model_id
    st.session_state.selected_device = dev
    st.session_state.current_view = "device_detail"


# ==========================================
# 3. VALIDATION & CRUD HELPERS
# ==========================================
def parse_devices_text(raw_text: str, existing_devices: list = None) -> tuple[list, str]:
    """
    Phân tích chuỗi nhập thiết bị theo định dạng mỗi dòng:
    Ký hiệu | Tên thiết bị | Khái niệm | Nội dung chi tiết
    Cho phép trường Ký hiệu (symbol) để trống hoặc nhập '-' đối với các khái niệm không có ký hiệu (như Vòng).
    Bảo toàn device_id và real_images của các thiết bị hiện có khi chỉnh sửa.
    """
    existing_devices = existing_devices or []
    existing_by_key = {}
    for ed in existing_devices:
        key_pair = (ed.get("symbol", "").strip(), ed.get("name", "").strip())
        existing_by_key[key_pair] = ed
        existing_by_key[ed.get("name", "").strip()] = ed

    devices = []
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
    if not lines:
        return [], "Mô hình phải có ít nhất 1 thiết bị hoặc khái niệm."

    for idx, line in enumerate(lines, start=1):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            return [], (
                f"Dòng thứ {idx} thiếu trường thông tin. "
                "Vui lòng nhập đủ 4 phần: Ký hiệu (hoặc '-' nếu không có) | Tên thiết bị | Khái niệm | Nội dung chi tiết"
            )
        raw_symbol, name, concept, details = parts[0], parts[1], parts[2], parts[3]
        if not name or not concept or not details:
            return [], (
                f"Dòng thứ {idx}: Tên thiết bị, Khái niệm và Nội dung chi tiết không được để trống."
            )
        normalized_symbol = "" if raw_symbol == "-" else raw_symbol

        # Khôi phục device_id và real_images nếu thiết bị đã tồn tại trước đó
        matched_old = (
            existing_by_key.get((normalized_symbol, name))
            or existing_by_key.get(name)
            or (existing_devices[idx - 1] if idx - 1 < len(existing_devices) else None)
        )
        dev_id = matched_old["device_id"] if matched_old and "device_id" in matched_old else f"dev-{uuid.uuid4().hex[:8]}"
        real_imgs = matched_old.get("real_images", []) if matched_old else []

        devices.append({
            "device_id": dev_id,
            "symbol": normalized_symbol,
            "name": name,
            "concept": concept,
            "details": details,
            "real_images": real_imgs
        })
    return devices, ""


def format_devices_to_text(devices: list) -> str:
    """Chuyển danh sách thiết bị sang chuỗi để hiển thị trong form chỉnh sửa."""
    return "\n".join(
        f"{d.get('symbol') if d.get('symbol') else '-'} | {d.get('name', '')} | {d.get('concept', '')} | {d.get('details', '').replace(chr(10), ' ')}"
        for d in devices
    )


def validate_and_normalize_models_json(raw_data: list) -> tuple[list, str]:
    """Kiểm tra tính hợp lệ và chuẩn hóa danh sách mô hình khi Import từ file data.json."""
    if not isinstance(raw_data, list):
        return [], "Cấu trúc file JSON không hợp lệ (Dữ liệu gốc phải là một danh sách mảng `[...]`)."
    normalized = []
    for idx, item in enumerate(raw_data, start=1):
        if not isinstance(item, dict):
            return [], f"Phần tử thứ {idx} trong JSON không phải là một đối tượng (Object)."
        if not item.get("id") or not item.get("title") or "devices" not in item:
            return [], f"Phần tử thứ {idx} thiếu các trường bắt buộc (`id`, `title`, `devices`)."
        item.setdefault("category", "Chưa phân loại")
        item.setdefault("created_at", datetime.now().isoformat())
        item.setdefault("status", "completed")
        item.setdefault("symbol", "N/A")
        item.setdefault("concept", "")
        if "diagram_image" not in item or not isinstance(item["diagram_image"], str):
            item["diagram_image"] = ""
        if "hotspots" not in item or not isinstance(item["hotspots"], list):
            item["hotspots"] = []
        if not isinstance(item["devices"], list):
            return [], f"Trường `devices` của mô hình '{item.get('title')}' phải là một danh sách."
        for dev in item["devices"]:
            dev.setdefault("device_id", f"dev-{uuid.uuid4().hex[:8]}")
            dev.setdefault("symbol", "")
            dev.setdefault("name", "Thiết bị")
            dev.setdefault("concept", "")
            dev.setdefault("details", "")
            if "real_images" not in dev or not isinstance(dev["real_images"], list):
                dev["real_images"] = []
        normalized.append(item)
    return normalized, ""


# ==========================================
# 4. BẢN VẼ KỸ THUẬT SVG (HÌNH 1.1 & HÌNH 1.2) & SƠ ĐỒ KHOANH VÙNG TÙY CHỈNH
# ==========================================
def render_interactive_svg_diagram(model: dict) -> None:
    """
    Render bản vẽ kỹ thuật SVG (Hình 1.1 & Hình 1.2) có nhúng trực tiếp các điểm tương tác (hotspots):
    - Di chuột (hover) vào đúng vị trí ký hiệu trên bản vẽ: Hiển thị tooltip tên thiết bị và làm sáng ký hiệu.
    - Nhấn chuột trái (click) vào ký hiệu trên bản vẽ: Kích hoạt nút Streamlit tương ứng (hỗ trợ đa tầng selector) để nhảy sang trang chi tiết thiết bị.
    """
    diagram_type = model.get("diagram_type", "")
    model_id = model["id"]

    if diagram_type == "fig_1_1":
        svg_markup = """
        <svg viewBox="0 0 650 330" width="100%" height="310" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrow-h11" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#0f172a"/>
                </marker>
            </defs>

            <!-- HOTSPOT: DÂY DẪN -->
            <g class="svg-hotspot" data-dev-id="h11-daydan" data-sym="Dây dẫn" data-idx="2" data-name="Dây dẫn">
                <path d="M 160 115 L 160 65 L 480 65 L 480 120 M 480 200 L 480 255 L 160 255 L 160 205"
                      fill="none" stroke="transparent" stroke-width="24"/>
                <path class="wire-path" d="M 160 115 L 160 65 L 480 65 L 480 120 M 480 200 L 480 255 L 160 255 L 160 205"
                      fill="none" stroke="#0f172a" stroke-width="2.6"/>
                <text x="315" y="25" font-family="Times New Roman, serif" font-size="20" fill="#0f172a">Dây dẫn</text>
                <line x1="340" y1="32" x2="318" y2="61" stroke="#0f172a" stroke-width="2" marker-end="url(#arrow-h11)"/>
            </g>

            <!-- HOTSPOT: NGUỒN ĐIỆN -->
            <g class="svg-hotspot" data-dev-id="h11-nguon" data-sym="Nguồn" data-idx="0" data-name="Nguồn điện">
                <circle class="shape-elem" cx="160" cy="160" r="45" fill="#ffffff" stroke="#0f172a" stroke-width="2.6"/>
                <text x="160" y="166" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">Nguồn</text>
            </g>

            <!-- HOTSPOT: PHỤ TẢI (TẢI) -->
            <g class="svg-hotspot" data-dev-id="h11-tai" data-sym="Tải" data-idx="1" data-name="Phụ tải (Tải)">
                <rect x="420" y="115" width="90" height="90" fill="transparent"/>
                <rect class="shape-elem" x="466" y="120" width="28" height="80" fill="#ffffff" stroke="#0f172a" stroke-width="5"/>
                <text x="453" y="168" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">Tải</text>
            </g>

            <text x="325" y="305" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="19" fill="#0f172a">
                Hình 1.1 Mô hình mạch điện
            </text>
        </svg>
        """
    elif diagram_type == "fig_1_2":
        svg_markup = """
        <svg viewBox="0 0 700 370" width="100%" height="350" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrow-h12" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#0f172a"/>
                </marker>
            </defs>

            <!-- HOTSPOT: DÂY DẪN -->
            <g class="svg-hotspot" data-dev-id="h12-daydan" data-sym="Dây dẫn" data-idx="2" data-name="Dây dẫn nối mạch">
                <path d="M 140 162 L 140 60 L 215 60 M 285 60 L 350 60 M 350 60 L 415 60 M 485 60 L 560 60 L 560 162
                         M 140 206 L 140 285 L 350 285 M 560 206 L 560 285 L 350 285
                         M 350 60 L 350 155 M 350 225 L 350 285"
                      fill="none" stroke="transparent" stroke-width="20"/>
                <path class="wire-path"
                      d="M 140 162 L 140 60 L 215 60 M 285 60 L 350 60 M 350 60 L 415 60 M 485 60 L 560 60 L 560 162
                         M 140 206 L 140 285 L 350 285 M 560 206 L 560 285 L 350 285
                         M 350 60 L 350 155 M 350 225 L 350 285"
                      fill="none" stroke="#0f172a" stroke-width="2.4"/>
            </g>

            <!-- HOTSPOT: NGUỒN E1, E2 -->
            <g class="svg-hotspot" data-dev-id="h12-nguon" data-sym="E1, E2" data-idx="0" data-name="Nguồn điện (E1, E2)">
                <circle class="shape-elem" cx="140" cy="184" r="22" fill="#ffffff" stroke="#0f172a" stroke-width="2.4"/>
                <line x1="140" y1="201" x2="140" y2="168" stroke="#0f172a" stroke-width="2" marker-end="url(#arrow-h12)"/>
                <text x="110" y="191" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">E1</text>

                <circle class="shape-elem" cx="560" cy="184" r="22" fill="#ffffff" stroke="#0f172a" stroke-width="2.4"/>
                <line x1="560" y1="201" x2="560" y2="168" stroke="#0f172a" stroke-width="2" marker-end="url(#arrow-h12)"/>
                <text x="530" y="191" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">E2</text>
            </g>

            <!-- HOTSPOT: PHỤ TẢI / ĐIỆN TRỞ R1, R2, R3 -->
            <g class="svg-hotspot" data-dev-id="h12-tai" data-sym="R1, R2, R3" data-idx="1" data-name="Phụ tải / Điện trở (R1, R2, R3)">
                <rect class="shape-elem" x="215" y="49" width="70" height="22" fill="#ffffff" stroke="#0f172a" stroke-width="2.4"/>
                <text x="250" y="100" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">
                    R<tspan dy="5" font-size="15">1</tspan>
                </text>

                <rect class="shape-elem" x="415" y="49" width="70" height="22" fill="#ffffff" stroke="#0f172a" stroke-width="2.4"/>
                <text x="450" y="100" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">
                    R<tspan dy="5" font-size="15">2</tspan>
                </text>

                <rect class="shape-elem" x="339" y="155" width="22" height="70" fill="#ffffff" stroke="#0f172a" stroke-width="2.4"/>
                <text x="331" y="196" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">
                    R<tspan dy="5" font-size="15">3</tspan>
                </text>
            </g>

            <!-- HOTSPOT: NHÁNH (I1, I2, I3) -->
            <g class="svg-hotspot" data-dev-id="h12-nhanh" data-sym="Nhánh (I1, I2, I3)" data-idx="3" data-name="Nhánh mạch điện (Nhánh 1, Nhánh 2, Nhánh 3)">
                <rect x="205" y="105" width="90" height="52" fill="transparent"/>
                <line class="wire-path" x1="215" y1="118" x2="285" y2="118" stroke="#0f172a" stroke-width="2.2" marker-end="url(#arrow-h12)"/>
                <text x="250" y="146" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">
                    I<tspan dy="5" font-size="15">1</tspan>
                </text>

                <rect x="405" y="105" width="90" height="52" fill="transparent"/>
                <line class="wire-path" x1="415" y1="118" x2="485" y2="118" stroke="#0f172a" stroke-width="2.2" marker-end="url(#arrow-h12)"/>
                <text x="450" y="146" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">
                    I<tspan dy="5" font-size="15">2</tspan>
                </text>

                <rect x="268" y="150" width="45" height="80" fill="transparent"/>
                <line class="wire-path" x1="298" y1="155" x2="298" y2="225" stroke="#0f172a" stroke-width="2.2" marker-end="url(#arrow-h12)"/>
                <text x="290" y="198" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#0f172a">
                    I<tspan dy="5" font-size="15">3</tspan>
                </text>
            </g>

            <!-- HOTSPOT: NÚT A, NÚT B -->
            <g class="svg-hotspot" data-dev-id="h12-nut" data-sym="Nút A, Nút B" data-idx="4" data-name="Nút mạch điện (Nút A, Nút B)">
                <circle cx="350" cy="60" r="20" fill="transparent"/>
                <circle class="node-elem" cx="350" cy="60" r="6.5" fill="#0f172a"/>
                <text x="350" y="36" text-anchor="middle" font-family="Times New Roman, serif" font-size="22" font-weight="bold" fill="#0f172a">A</text>

                <circle cx="350" cy="285" r="20" fill="transparent"/>
                <circle class="node-elem" cx="350" cy="285" r="6.5" fill="#0f172a"/>
                <text x="350" y="320" text-anchor="middle" font-family="Times New Roman, serif" font-size="22" font-weight="bold" fill="#0f172a">B</text>
            </g>

            <text x="350" y="355" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="19" fill="#0f172a">
                Hình 1.2 Kết cấu hình học của mạch điện
            </text>
        </svg>
        """
    else:
        svg_markup = ""

    if not svg_markup:
        return

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 6px;
                font-family: system-ui, -apple-system, sans-serif;
                background: transparent;
                display: flex;
                flex-direction: column;
                align-items: center;
                user-select: none;
            }}
            .diagram-box {{
                position: relative;
                width: 100%;
                max-width: 680px;
                border: 2px solid #38bdf8;
                border-radius: 12px;
                background-color: #f8fafc;
                background-image:
                    linear-gradient(rgba(14, 165, 233, 0.08) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(14, 165, 233, 0.08) 1px, transparent 1px);
                background-size: 20px 20px;
                box-shadow: 0 0 24px rgba(56, 189, 248, 0.25);
                padding: 10px;
            }}
            .svg-hotspot {{
                cursor: pointer;
                transition: all 0.18s ease;
            }}
            .svg-hotspot:hover .shape-elem {{
                stroke: #0284c7 !important;
                fill: #e0f2fe !important;
                filter: drop-shadow(0 0 6px rgba(2, 132, 199, 0.55));
            }}
            .svg-hotspot:hover .wire-path {{
                stroke: #0284c7 !important;
                stroke-width: 4px !important;
                filter: drop-shadow(0 0 5px rgba(2, 132, 199, 0.5));
            }}
            .svg-hotspot:hover .node-elem {{
                fill: #0284c7 !important;
                r: 8.5px;
                filter: drop-shadow(0 0 7px rgba(2, 132, 199, 0.7));
            }}
            .svg-hotspot:hover text {{
                fill: #0369a1 !important;
                font-weight: bold;
            }}
            #floating-tooltip {{
                position: fixed;
                display: none;
                background: rgba(15, 23, 42, 0.96);
                color: #f8fafc;
                padding: 7px 13px;
                border-radius: 7px;
                font-size: 13.5px;
                font-weight: 500;
                pointer-events: none;
                z-index: 9999;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
                border: 1px solid #38bdf8;
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <div class="diagram-box">
            {svg_markup}
        </div>
        <div id="floating-tooltip"></div>

        <script>
            const tooltip = document.getElementById('floating-tooltip');
            const hotspots = document.querySelectorAll('.svg-hotspot');
            const modelId = "{model_id}";

            function triggerStreamlitSymbolButton(devId, symText, idx) {{
                const parentDoc = window.parent.document;
                let btn = null;

                // Tầng 1: Tìm theo class st-key của Streamlit
                const keyClass = 'st-key-modal_sym_' + modelId + '_' + devId;
                const keyContainer = parentDoc.querySelector('.' + keyClass);
                if (keyContainer) {{
                    btn = keyContainer.querySelector('button');
                }}

                // Tầng 2: Tìm nút trong Dialog khớp chính xác nhãn ký hiệu "🔣 " + symText
                if (!btn && symText) {{
                    const dialogScope = parentDoc.querySelector('[role="dialog"], [data-testid="stDialog"]') || parentDoc;
                    const allBtns = dialogScope.querySelectorAll('button');
                    for (const b of allBtns) {{
                        const txt = (b.innerText || b.textContent || '').trim();
                        if (txt === '🔣 ' + symText || txt.includes(symText)) {{
                            btn = b;
                            break;
                        }}
                    }}
                }}

                // Tầng 3: Tìm theo thứ tự nút ký hiệu "🔣" trong Dialog
                if (!btn && idx !== null && !isNaN(idx)) {{
                    const dialogScope = parentDoc.querySelector('[role="dialog"], [data-testid="stDialog"]') || parentDoc;
                    const symBtns = Array.from(dialogScope.querySelectorAll('button')).filter(
                        b => (b.innerText || b.textContent || '').includes('🔣')
                    );
                    if (symBtns[idx]) {{
                        btn = symBtns[idx];
                    }}
                }}

                if (btn) {{
                    btn.click();
                }}
            }}

            hotspots.forEach(group => {{
                group.addEventListener('mousemove', (e) => {{
                    const devName = group.getAttribute('data-name');
                    tooltip.innerHTML = "⚡ <b>" + devName + "</b> <span style='color:#38bdf8;font-size:12px;'>(Nhấn chuột trái để xem chi tiết)</span>";
                    tooltip.style.display = 'block';
                    let leftPos = e.clientX + 14;
                    let topPos = e.clientY - 36;
                    if (leftPos + 290 > window.innerWidth) {{
                        leftPos = e.clientX - 270;
                    }}
                    if (topPos < 8) {{
                        topPos = e.clientY + 18;
                    }}
                    tooltip.style.left = leftPos + 'px';
                    tooltip.style.top = topPos + 'px';
                }});

                group.addEventListener('mouseleave', () => {{
                    tooltip.style.display = 'none';
                }});

                group.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    const devId = group.getAttribute('data-dev-id');
                    const symText = group.getAttribute('data-sym');
                    const idx = parseInt(group.getAttribute('data-idx'), 10);
                    triggerStreamlitSymbolButton(devId, symText, idx);
                }});
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=385 if diagram_type == "fig_1_2" else 345, scrolling=False)


def render_custom_image_diagram(model: dict) -> None:
    """
    Hiển thị ảnh sơ đồ mô hình tùy chỉnh kèm các vùng đánh dấu ký hiệu (hotspots) đã được khoanh tay:
    - Di chuột (hover) vào vùng khoanh: Làm sáng vùng ký hiệu và hiện tooltip tên thiết bị.
    - Nhấn chuột trái (click) vào vùng khoanh: Kích hoạt nút thiết bị tương ứng để chuyển sang trang chi tiết.
    """
    diagram_img = model.get("diagram_image", "").strip()
    if not diagram_img:
        return

    model_id = model["id"]
    devices = model.get("devices", [])
    symbol_devices = [d for d in devices if d.get("symbol", "").strip()]
    sym_idx_map = {d["device_id"]: idx for idx, d in enumerate(symbol_devices)}
    dev_map = {d["device_id"]: d for d in devices}

    hotspots = model.get("hotspots", [])
    hotspot_divs = []
    for hs in hotspots:
        dev_id = hs.get("device_id", "")
        dev_info = dev_map.get(dev_id, {})
        dev_name = dev_info.get("name") or hs.get("name", "Thiết bị")
        dev_sym = dev_info.get("symbol") or hs.get("symbol", "")
        sym_idx = sym_idx_map.get(dev_id, -1)
        x = float(hs.get("x", 0))
        y = float(hs.get("y", 0))
        w = float(hs.get("w", 10))
        h = float(hs.get("h", 10))
        safe_name = dev_name.replace('"', "&quot;")
        safe_sym = dev_sym.replace('"', "&quot;")
        label_badge = dev_sym if dev_sym else dev_name

        hotspot_divs.append(
            f'<div class="custom-hs-box" '
            f'data-dev-id="{dev_id}" data-sym="{safe_sym}" data-idx="{sym_idx}" data-name="{safe_name}" '
            f'style="left:{x}%; top:{y}%; width:{w}%; height:{h}%;">'
            f'<span class="hs-tag">{label_badge}</span>'
            f'</div>'
        )

    hotspots_html = "\n".join(hotspot_divs)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 6px;
                font-family: system-ui, -apple-system, sans-serif;
                background: transparent;
                display: flex;
                flex-direction: column;
                align-items: center;
                user-select: none;
            }}
            .custom-diagram-wrapper {{
                position: relative;
                display: inline-block;
                max-width: 680px;
                width: 100%;
                border: 2px solid #38bdf8;
                border-radius: 12px;
                background: #f8fafc;
                box-shadow: 0 0 24px rgba(56, 189, 248, 0.25);
                overflow: hidden;
            }}
            .custom-diagram-wrapper img {{
                display: block;
                width: 100%;
                height: auto;
                max-height: 400px;
                object-fit: contain;
                background: #ffffff;
            }}
            .custom-hs-box {{
                position: absolute;
                border: 2px dashed rgba(2, 132, 199, 0.75);
                background: rgba(56, 189, 248, 0.14);
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.18s ease;
                box-sizing: border-box;
            }}
            .custom-hs-box:hover {{
                border: 2.5px solid #0284c7;
                background: rgba(14, 165, 233, 0.32);
                box-shadow: 0 0 14px rgba(2, 132, 199, 0.75);
                transform: scale(1.015);
                z-index: 20;
            }}
            .hs-tag {{
                position: absolute;
                top: -20px;
                left: 0;
                background: rgba(15, 23, 42, 0.9);
                color: #38bdf8;
                font-size: 11px;
                font-weight: 600;
                padding: 1px 6px;
                border-radius: 4px;
                border: 1px solid rgba(56, 189, 248, 0.5);
                white-space: nowrap;
                pointer-events: none;
            }}
            #custom-floating-tooltip {{
                position: fixed;
                display: none;
                background: rgba(15, 23, 42, 0.96);
                color: #f8fafc;
                padding: 7px 13px;
                border-radius: 7px;
                font-size: 13.5px;
                font-weight: 500;
                pointer-events: none;
                z-index: 9999;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
                border: 1px solid #38bdf8;
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <div class="custom-diagram-wrapper">
            <img src="{diagram_img}" alt="Sơ đồ mô hình" />
            {hotspots_html}
        </div>
        <div id="custom-floating-tooltip"></div>

        <script>
            const tooltip = document.getElementById('custom-floating-tooltip');
            const boxes = document.querySelectorAll('.custom-hs-box');
            const modelId = "{model_id}";

            function triggerStreamlitDeviceButton(devId, symText, idx) {{
                const parentDoc = window.parent.document;
                let btn = null;

                // Tầng 1: Tìm theo key nút có ký hiệu hoặc nút không ký hiệu
                const symKey = 'st-key-modal_sym_' + modelId + '_' + devId;
                const noSymKey = 'st-key-modal_nosym_' + modelId + '_' + devId;
                const keyContainer = parentDoc.querySelector('.' + symKey) || parentDoc.querySelector('.' + noSymKey);
                if (keyContainer) {{
                    btn = keyContainer.querySelector('button');
                }}

                // Tầng 2: Tìm theo nhãn văn bản ký hiệu
                if (!btn && symText) {{
                    const dialogScope = parentDoc.querySelector('[role="dialog"], [data-testid="stDialog"]') || parentDoc;
                    const allBtns = dialogScope.querySelectorAll('button');
                    for (const b of allBtns) {{
                        const txt = (b.innerText || b.textContent || '').trim();
                        if (txt === '🔣 ' + symText || txt.includes(symText)) {{
                            btn = b;
                            break;
                        }}
                    }}
                }}

                // Tầng 3: Tìm theo thứ tự nút ký hiệu
                if (!btn && idx !== null && !isNaN(idx) && idx >= 0) {{
                    const dialogScope = parentDoc.querySelector('[role="dialog"], [data-testid="stDialog"]') || parentDoc;
                    const symBtns = Array.from(dialogScope.querySelectorAll('button')).filter(
                        b => (b.innerText || b.textContent || '').includes('🔣')
                    );
                    if (symBtns[idx]) {{
                        btn = symBtns[idx];
                    }}
                }}

                if (btn) {{
                    btn.click();
                }}
            }}

            boxes.forEach(box => {{
                box.addEventListener('mousemove', (e) => {{
                    const devName = box.getAttribute('data-name');
                    tooltip.innerHTML = "⚡ <b>" + devName + "</b> <span style='color:#38bdf8;font-size:12px;'>(Nhấn chuột trái để xem chi tiết)</span>";
                    tooltip.style.display = 'block';
                    let leftPos = e.clientX + 14;
                    let topPos = e.clientY - 36;
                    if (leftPos + 290 > window.innerWidth) {{
                        leftPos = e.clientX - 270;
                    }}
                    if (topPos < 8) {{
                        topPos = e.clientY + 18;
                    }}
                    tooltip.style.left = leftPos + 'px';
                    tooltip.style.top = topPos + 'px';
                }});

                box.addEventListener('mouseleave', () => {{
                    tooltip.style.display = 'none';
                }});

                box.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    const devId = box.getAttribute('data-dev-id');
                    const symText = box.getAttribute('data-sym');
                    const idx = parseInt(box.getAttribute('data-idx'), 10);
                    triggerStreamlitDeviceButton(devId, symText, idx);
                }});
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=430, scrolling=False)


def sync_model_diagram_and_hotspots(model_id: str, diagram_image: str = None, hotspots: list = None) -> None:
    """Cập nhật ảnh sơ đồ mô hình (diagram_image) và danh sách vùng đánh dấu (hotspots) vào bộ nhớ và data.json."""
    for item in st.session_state.models_data:
        if item["id"] == model_id:
            if diagram_image is not None:
                item["diagram_image"] = diagram_image
            if hotspots is not None:
                item["hotspots"] = hotspots
            break
    save_data(st.session_state.models_data)


def render_visual_hotspot_editor_widget(model: dict, context_key: str = "editor") -> None:
    """
    Giao diện công cụ tải ảnh sơ đồ mô hình & kéo chuột khoanh vùng đánh dấu ký hiệu bằng tay (Visual Hotspot Editor).
    """
    model_id = model["id"]
    devices = model.get("devices", [])

    # 1. Khu vực tải lên hoặc cập nhật ảnh sơ đồ mô hình
    with st.container(border=True):
        st.markdown("##### 🖼️ Bước 1: Tải ảnh sơ đồ mô hình (hoặc dán URL ảnh)")
        up_col1, up_col2 = st.columns([1.4, 1])
        with up_col1:
            uploaded_diag = st.file_uploader(
                "Chọn file ảnh sơ đồ (.png, .jpg, .jpeg, .webp)",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"diag_file_{context_key}_{model_id}"
            )
        with up_col2:
            diag_url = st.text_input(
                "Hoặc nhập URL ảnh sơ đồ",
                value=model.get("diagram_image", "") if model.get("diagram_image", "").startswith("http") else "",
                placeholder="https://example.com/circuit-diagram.png",
                key=f"diag_url_{context_key}_{model_id}"
            )

        btn_img_col1, btn_img_col2 = st.columns([1, 1])
        with btn_img_col1:
            if st.button("📸 Cập nhật ảnh sơ đồ", key=f"btn_save_diag_{context_key}_{model_id}", type="primary", use_container_width=True):
                if uploaded_diag is not None:
                    mime = uploaded_diag.type or "image/png"
                    b64_str = base64.b64encode(uploaded_diag.getvalue()).decode("utf-8")
                    new_img_src = f"data:{mime};base64,{b64_str}"
                    sync_model_diagram_and_hotspots(model_id, diagram_image=new_img_src)
                    st.toast("Đã tải lên ảnh sơ đồ mô hình thành công!", icon="✅")
                    st.rerun()
                elif diag_url.strip():
                    sync_model_diagram_and_hotspots(model_id, diagram_image=diag_url.strip())
                    st.toast("Đã cập nhật URL ảnh sơ đồ thành công!", icon="✅")
                    st.rerun()
                else:
                    st.error("Vui lòng chọn 1 file ảnh hoặc nhập đường dẫn URL ảnh sơ đồ!")
        with btn_img_col2:
            if model.get("diagram_image") and st.button(
                "🗑️ Xóa ảnh sơ đồ tùy chỉnh",
                key=f"btn_del_diag_{context_key}_{model_id}",
                use_container_width=True
            ):
                sync_model_diagram_and_hotspots(model_id, diagram_image="", hotspots=[])
                st.toast("Đã xóa ảnh sơ đồ tùy chỉnh và các vùng khoanh!", icon="🗑️")
                st.rerun()

    current_img = model.get("diagram_image", "").strip()
    if not current_img:
        st.info(
            "💡 Mô hình này chưa có ảnh sơ đồ tùy chỉnh. Hãy tải lên 1 ảnh sơ đồ ở **Bước 1** phía trên để bắt đầu kéo chuột khoanh vùng đánh dấu ký hiệu bằng tay "
            "(Hai bản vẽ SVG gốc **Hình 1.1** và **Hình 1.2** vẫn luôn được giữ nguyên 100%)."
        )
        return

    if not devices:
        st.warning("Mô hình này chưa có thiết bị nào. Vui lòng thêm thiết bị vào mô hình trước khi khoanh vùng ký hiệu.")
        return

    # 2. Khu vực kéo chuột khoanh vùng ký hiệu trực tiếp trên ảnh
    st.markdown("##### 🎯 Bước 2: Chọn Thiết bị & Kéo chuột trái trên ảnh sơ đồ để khoanh vùng ký hiệu")
    st.caption(
        "Hướng dẫn: Chọn thiết bị ở thanh công cụ bên dưới ➡️ Nhấn giữ và kéo chuột trái trên ảnh để tạo vùng đánh dấu ➡️ "
        "Nhấn nút **💾 Lưu vùng khoanh ký hiệu** để hoàn tất."
    )

    devices_json = json.dumps(
        [{"device_id": d["device_id"], "symbol": d.get("symbol", ""), "name": d.get("name", "")} for d in devices],
        ensure_ascii=False
    )
    initial_hotspots_json = json.dumps(model.get("hotspots", []), ensure_ascii=False)
    bridge_key = f"hs_bridge_{context_key}_{model_id}"
    save_btn_key = f"hs_save_btn_{context_key}_{model_id}"

    editor_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 8px;
                font-family: system-ui, -apple-system, sans-serif;
                background: #0f172a;
                color: #f8fafc;
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 12px;
                user-select: none;
            }}
            .toolbar {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                align-items: center;
                justify-content: space-between;
                background: rgba(30, 41, 59, 0.9);
                padding: 10px 12px;
                border-radius: 8px;
                border: 1px solid rgba(56, 189, 248, 0.25);
                margin-bottom: 10px;
            }}
            .toolbar select {{
                background: #0f172a;
                color: #38bdf8;
                border: 1px solid #38bdf8;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13.5px;
                font-weight: 600;
                flex: 1;
                min-width: 210px;
            }}
            .btn-tool {{
                background: #1e293b;
                color: #e2e8f0;
                border: 1px solid rgba(148, 163, 184, 0.4);
                border-radius: 6px;
                padding: 6px 11px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.15s;
            }}
            .btn-tool:hover {{
                border-color: #38bdf8;
                color: #38bdf8;
            }}
            .btn-save-now {{
                background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
                color: #ffffff;
                border: 1px solid #7dd3fc;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
            }}
            .btn-save-now:hover {{
                filter: brightness(1.1);
            }}
            .canvas-stage-wrap {{
                display: flex;
                justify-content: center;
                background: #070d19;
                padding: 10px;
                border-radius: 8px;
                border: 1px dashed rgba(56, 189, 248, 0.35);
            }}
            #img-stage {{
                position: relative;
                display: inline-block;
                max-width: 100%;
                cursor: crosshair;
                line-height: 0;
            }}
            #img-stage img {{
                display: block;
                max-width: 100%;
                max-height: 360px;
                width: auto;
                height: auto;
                background: #ffffff;
                border-radius: 6px;
                pointer-events: none;
            }}
            .drawn-box {{
                position: absolute;
                border: 2px solid #0284c7;
                background: rgba(14, 165, 233, 0.24);
                border-radius: 4px;
                box-sizing: border-box;
            }}
            .drawn-box-label {{
                position: absolute;
                top: -19px;
                left: 0;
                background: #0f172a;
                color: #7dd3fc;
                font-size: 11px;
                font-weight: 600;
                padding: 2px 6px;
                border-radius: 4px;
                border: 1px solid #38bdf8;
                white-space: nowrap;
                line-height: 1.2;
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            .del-hs-btn {{
                color: #f87171;
                cursor: pointer;
                font-weight: bold;
                margin-left: 4px;
            }}
            #rubber-band {{
                position: absolute;
                display: none;
                border: 2px dashed #22d3ee;
                background: rgba(34, 211, 238, 0.25);
                pointer-events: none;
                box-sizing: border-box;
            }}
            .status-bar {{
                margin-top: 8px;
                font-size: 12.5px;
                color: #94a3b8;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
        </style>
    </head>
    <body>
        <div class="toolbar">
            <select id="device-select"></select>
            <button type="button" class="btn-tool" id="undo-btn">↩️ Hoàn tác</button>
            <button type="button" class="btn-tool" id="clear-btn">🗑️ Xóa hết vùng</button>
            <button type="button" class="btn-save-now" id="apply-save-btn">💾 Áp dụng & Lưu vùng khoanh</button>
        </div>

        <div class="canvas-stage-wrap">
            <div id="img-stage">
                <img id="diagram-img" src="{current_img}" draggable="false" />
                <div id="boxes-layer"></div>
                <div id="rubber-band"></div>
            </div>
        </div>

        <div class="status-bar">
            <span id="hs-count-info">Đang tải...</span>
            <span style="color:#38bdf8;">💡 Mẹo: Kéo chuột trái trên ảnh để vẽ khung khoanh vùng ký hiệu</span>
        </div>

        <script>
            const devices = {devices_json};
            let hotspots = {initial_hotspots_json};
            const bridgeKeyClass = "st-key-{bridge_key}";
            const saveBtnKeyClass = "st-key-{save_btn_key}";

            const selectEl = document.getElementById('device-select');
            const stageEl = document.getElementById('img-stage');
            const boxesLayer = document.getElementById('boxes-layer');
            const rubberBand = document.getElementById('rubber-band');
            const countInfo = document.getElementById('hs-count-info');

            devices.forEach((d) => {{
                const opt = document.createElement('option');
                opt.value = d.device_id;
                const symLabel = d.symbol ? ("[" + d.symbol + "] ") : "[Không ký hiệu] ";
                opt.textContent = symLabel + d.name;
                selectEl.appendChild(opt);
            }});

            function syncToStreamlitInput() {{
                const jsonStr = JSON.stringify(hotspots);
                const parentDoc = window.parent.document;
                const container = parentDoc.querySelector('.' + bridgeKeyClass);
                if (!container) return;
                const inputEl = container.querySelector('input, textarea');
                if (!inputEl) return;

                const proto = inputEl.tagName === 'TEXTAREA'
                    ? window.parent.HTMLTextAreaElement.prototype
                    : window.parent.HTMLInputElement.prototype;
                const nativeSetter = Object.getOwnPropertyDescriptor(proto, 'value').set;
                nativeSetter.call(inputEl, jsonStr);
                inputEl.dispatchEvent(new Event('input', {{ bubbles: true }}));
                inputEl.dispatchEvent(new Event('change', {{ bubbles: true }}));
                inputEl.dispatchEvent(new KeyboardEvent('keydown', {{
                    key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                }}));
                inputEl.blur();
            }}

            function renderBoxes() {{
                boxesLayer.innerHTML = '';
                hotspots.forEach((hs, index) => {{
                    const box = document.createElement('div');
                    box.className = 'drawn-box';
                    box.style.left = hs.x + '%';
                    box.style.top = hs.y + '%';
                    box.style.width = hs.w + '%';
                    box.style.height = hs.h + '%';

                    const label = document.createElement('div');
                    label.className = 'drawn-box-label';
                    const tagText = hs.symbol ? (hs.symbol + ' (' + hs.name + ')') : hs.name;
                    label.innerHTML = '<span>' + tagText + '</span>';

                    const delBtn = document.createElement('span');
                    delBtn.className = 'del-hs-btn';
                    delBtn.textContent = '✕';
                    delBtn.title = 'Xóa vùng này';
                    delBtn.addEventListener('mousedown', (ev) => {{ ev.stopPropagation(); }});
                    delBtn.addEventListener('click', (ev) => {{
                        ev.stopPropagation();
                        hotspots.splice(index, 1);
                        renderBoxes();
                        syncToStreamlitInput();
                    }});

                    label.appendChild(delBtn);
                    box.appendChild(label);
                    boxesLayer.appendChild(box);
                }});
                countInfo.textContent = "Đã khoanh " + hotspots.length + " vùng ký hiệu trên sơ đồ.";
            }}

            let isDrawing = false;
            let startX = 0;
            let startY = 0;

            stageEl.addEventListener('mousedown', (e) => {{
                if (e.button !== 0) return;
                const rect = stageEl.getBoundingClientRect();
                if (rect.width <= 0 || rect.height <= 0) return;
                isDrawing = true;
                startX = e.clientX - rect.left;
                startY = e.clientY - rect.top;
                rubberBand.style.left = startX + 'px';
                rubberBand.style.top = startY + 'px';
                rubberBand.style.width = '0px';
                rubberBand.style.height = '0px';
                rubberBand.style.display = 'block';
            }});

            window.addEventListener('mousemove', (e) => {{
                if (!isDrawing) return;
                const rect = stageEl.getBoundingClientRect();
                let curX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
                let curY = Math.max(0, Math.min(e.clientY - rect.top, rect.height));
                const left = Math.min(startX, curX);
                const top = Math.min(startY, curY);
                const width = Math.abs(curX - startX);
                const height = Math.abs(curY - startY);
                rubberBand.style.left = left + 'px';
                rubberBand.style.top = top + 'px';
                rubberBand.style.width = width + 'px';
                rubberBand.style.height = height + 'px';
            }});

            window.addEventListener('mouseup', (e) => {{
                if (!isDrawing) return;
                isDrawing = false;
                rubberBand.style.display = 'none';

                const rect = stageEl.getBoundingClientRect();
                if (rect.width <= 0 || rect.height <= 0) return;
                let curX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
                let curY = Math.max(0, Math.min(e.clientY - rect.top, rect.height));
                const leftPx = Math.min(startX, curX);
                const topPx = Math.min(startY, curY);
                const widthPx = Math.abs(curX - startX);
                const heightPx = Math.abs(curY - startY);

                // Bỏ qua nếu vùng kéo quá nhỏ (< 8px)
                if (widthPx < 8 || heightPx < 8) return;

                const selectedDevId = selectEl.value;
                const devObj = devices.find(d => d.device_id === selectedDevId) || devices[0];

                const xPct = Math.round((leftPx / rect.width) * 10000) / 100;
                const yPct = Math.round((topPx / rect.height) * 10000) / 100;
                const wPct = Math.round((widthPx / rect.width) * 10000) / 100;
                const hPct = Math.round((heightPx / rect.height) * 10000) / 100;

                hotspots.push({{
                    hotspot_id: 'hs-' + Date.now() + '-' + Math.floor(Math.random() * 1000),
                    device_id: devObj.device_id,
                    symbol: devObj.symbol || '',
                    name: devObj.name || 'Thiết bị',
                    x: xPct,
                    y: yPct,
                    w: wPct,
                    h: hPct
                }});

                renderBoxes();
                syncToStreamlitInput();
            }});

            document.getElementById('undo-btn').addEventListener('click', () => {{
                if (hotspots.length > 0) {{
                    hotspots.pop();
                    renderBoxes();
                    syncToStreamlitInput();
                }}
            }});

            document.getElementById('clear-btn').addEventListener('click', () => {{
                hotspots = [];
                renderBoxes();
                syncToStreamlitInput();
            }});

            document.getElementById('apply-save-btn').addEventListener('click', () => {{
                syncToStreamlitInput();
                setTimeout(() => {{
                    const parentDoc = window.parent.document;
                    const saveContainer = parentDoc.querySelector('.' + saveBtnKeyClass);
                    if (saveContainer) {{
                        const btn = saveContainer.querySelector('button');
                        if (btn) btn.click();
                    }}
                }}, 150);
            }});

            renderBoxes();
        </script>
    </body>
    </html>
    """
    components.html(editor_html, height=485, scrolling=False)

    # Cầu nối dữ liệu JSON tọa độ giữa JS Canvas và Streamlit
    raw_hs_json = st.text_input(
        "Dữ liệu tọa độ vùng đánh dấu (Tự động đồng bộ khi kéo chuột)",
        value=initial_hotspots_json,
        key=bridge_key,
        help="Tọa độ các vùng khoanh ký hiệu được tự động cập nhật vào ô này khi bạn kéo chuột trên ảnh."
    )

    if st.button(
        "💾 Lưu vùng khoanh ký hiệu (Save Hotspots)",
        key=save_btn_key,
        type="primary",
        use_container_width=True
    ):
        try:
            parsed_hs = json.loads(raw_hs_json) if raw_hs_json.strip() else []
            if not isinstance(parsed_hs, list):
                st.error("Dữ liệu vùng đánh dấu không hợp lệ!")
            else:
                sync_model_diagram_and_hotspots(model_id, hotspots=parsed_hs)
                st.toast(f"Đã lưu {len(parsed_hs)} vùng đánh dấu ký hiệu thành công!", icon="🎯")
                try:
                    st.rerun(scope="app")
                except TypeError:
                    st.rerun()
        except json.JSONDecodeError:
            st.error("Lỗi định dạng JSON tọa độ vùng đánh dấu!")


@st.dialog("🎯 Visual Hotspot Editor — Tải ảnh & Khoanh vùng Ký hiệu", width="large")
def open_hotspot_editor_modal(model: dict):
    """Hộp thoại chuyên biệt để tải ảnh sơ đồ mô hình và kéo chuột khoanh vùng ký hiệu bằng tay."""
    latest_model = next((m for m in st.session_state.models_data if m["id"] == model["id"]), model)
    st.subheader(f"📐 {latest_model['title']} (`{latest_model.get('symbol', 'N/A')}`)")
    render_visual_hotspot_editor_widget(latest_model, context_key="standalone_modal")


# ==========================================
# 5. DIALOGS (MODALS): TƯƠNG TÁC MÔ HÌNH & FORM CRUD
# ==========================================
@st.dialog("🔍 Sơ đồ Mô hình & Ký hiệu Thiết bị", width="large")
def open_model_modal(model: dict):
    """
    Modal hiển thị mô hình với bản vẽ kỹ thuật SVG (Hình 1.1, Hình 1.2), sơ đồ khoanh vùng tùy chỉnh
    và các 'Ký hiệu thiết bị' tương tác:
    - Di chuột (hover) vào ký hiệu trên bản vẽ hoặc nút: Xem tên thiết bị.
    - Nhấn chuột trái vào ký hiệu trên bản vẽ hoặc nút: Chuyển ngay sang trang chi tiết của thiết bị.
    - Các khái niệm không có ký hiệu (như Vòng) hiển thị ở mục Khái niệm bên dưới.
    """
    # Nếu callback chuyển trang đã được kích hoạt từ nút bên trong Dialog, thực hiện rerun toàn bộ ứng dụng ngay lập tức
    if st.session_state.current_view == "device_detail":
        try:
            st.rerun(scope="app")
        except TypeError:
            st.rerun()

    latest_model = next((m for m in st.session_state.models_data if m["id"] == model["id"]), model)

    st.subheader(f"📐 {latest_model['title']} (`{latest_model.get('symbol', 'N/A')}`)")
    st.caption(f"Phân loại: {latest_model['category']} | Trạng thái: {latest_model['status']}")
    st.markdown(f"**Khái niệm mô hình:** {latest_model.get('concept', '')}")
    st.divider()

    st.markdown(
        "💡 *Hướng dẫn: **Di chuột** trực tiếp vào các ký hiệu trên bản vẽ kỹ thuật (Nguồn, Tải, Dây dẫn, Nhánh, Nút) "
        "để xem tên thiết bị. **Nhấn chuột trái** vào ký hiệu để chuyển sang trang nội dung chi tiết.*"
    )

    devices = latest_model.get("devices", [])
    if not devices:
        st.info("Mô hình này chưa có thiết bị nào.")
        return

    symbol_devices = [d for d in devices if d.get("symbol", "").strip()]
    non_symbol_devices = [d for d in devices if not d.get("symbol", "").strip()]

    # 1. Hiển thị bản vẽ kỹ thuật SVG gốc (Giữ nguyên 100% Hình 1.1 & Hình 1.2)
    if latest_model.get("diagram_type") in ("fig_1_1", "fig_1_2"):
        render_interactive_svg_diagram(latest_model)

    # 1b. Hiển thị ảnh sơ đồ tùy chỉnh có khoanh vùng Hotspot (nếu người dùng đã tải lên cho mô hình)
    if latest_model.get("diagram_image", "").strip():
        st.markdown("##### 🖼️ Sơ đồ Mô hình Tùy chỉnh (Tương tác qua vùng đã khoanh)")
        render_custom_image_diagram(latest_model)

    # 2. Hiển thị hàng nút Ký hiệu thiết bị có gắn on_click callback đảm bảo nhảy trang 100%
    if symbol_devices:
        with st.container(border=True):
            st.markdown("##### ⚡ Các Ký hiệu Thiết bị trên Mô hình (Nhấn trực tiếp trên bản vẽ hoặc nút ký hiệu bên dưới)")
            cols = st.columns(len(symbol_devices))
            for idx, dev in enumerate(symbol_devices):
                with cols[idx]:
                    if st.button(
                        f"🔣 {dev['symbol']}",
                        key=f"modal_sym_{latest_model['id']}_{dev['device_id']}",
                        help=f"Tên thiết bị: {dev['name']} (Nhấn chuột trái để xem chi tiết)",
                        on_click=navigate_to_device_detail,
                        args=(latest_model["id"], dev),
                        use_container_width=True,
                        type="primary"
                    ):
                        try:
                            st.rerun(scope="app")
                        except TypeError:
                            st.rerun()

    # 3. Hiển thị các khái niệm không có ký hiệu trên hình (VD: Vòng / Mạch vòng)
    if non_symbol_devices:
        with st.container(border=True):
            st.markdown("##### 📘 Khái niệm thuộc mô hình (Không có ký hiệu riêng trên hình)")
            for dev in non_symbol_devices:
                col_info, col_act = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**{dev['name']}:** {dev.get('concept', '')}")
                    if dev.get("details"):
                        st.caption(dev["details"])
                with col_act:
                    if st.button(
                        "📄 Xem chi tiết",
                        key=f"modal_nosym_{latest_model['id']}_{dev['device_id']}",
                        help=f"Xem trang chi tiết: {dev['name']}",
                        on_click=navigate_to_device_detail,
                        args=(latest_model["id"], dev),
                        use_container_width=True
                    ):
                        try:
                            st.rerun(scope="app")
                        except TypeError:
                            st.rerun()

    # 4. Tích hợp công cụ Visual Hotspot Editor ngay trong Modal để tiện chỉnh sửa trực tiếp
    with st.expander("🎯 Công cụ tải ảnh sơ đồ & Kéo chuột khoanh vùng ký hiệu bằng tay (Visual Hotspot Editor)", expanded=False):
        render_visual_hotspot_editor_widget(latest_model, context_key="in_model_modal")


@st.dialog("📝 Thêm / Chỉnh sửa Mô hình ĐĐT", width="large")
def open_crud_modal(edit_model: dict = None):
    """
    Dialog Form Thêm/Sửa Mô hình với kiểm tra dữ liệu (Validation) chặt chẽ bằng st.error.
    Hỗ trợ đính kèm ảnh sơ đồ mô hình ngay khi tạo/sửa.
    """
    is_edit = edit_model is not None
    default_title = edit_model["title"] if is_edit else ""
    default_symbol = edit_model.get("symbol", "") if is_edit else ""
    default_category = edit_model["category"] if is_edit else "1.1. Các khái niệm cơ bản trong mạch điện"
    default_status = edit_model["status"] if is_edit else "completed"
    default_concept = edit_model.get("concept", "") if is_edit else ""
    default_devices_txt = (
        format_devices_to_text(edit_model.get("devices", []))
        if is_edit
        else "Nguồn | Nguồn điện | Thiết bị tạo ra điện năng | Pin, ắc quy, máy phát điện\n- | Vòng (mạch vòng) | Đường dẫn khép kín qua các phần tử | Không có ký hiệu riêng trên sơ đồ"
    )

    with st.form(key="crud_model_form", clear_on_submit=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            title = st.text_input("Tên mô hình (*)", value=default_title, placeholder="VD: Hình 1.1: Mô hình mạch điện")
        with col2:
            symbol = st.text_input("Ký hiệu mô hình (*)", value=default_symbol, placeholder="VD: H1.1")

        col3, col4 = st.columns([2, 1])
        with col3:
            category = st.text_input("Danh mục / Học phần (*)", value=default_category)
        with col4:
            status = st.selectbox(
                "Trạng thái (*)",
                options=["pending", "completed"],
                index=0 if default_status == "pending" else 1
            )

        concept = st.text_area(
            "Khái niệm & Nguyên lý mô hình (*)",
            value=default_concept,
            placeholder="Mô tả khái niệm và nguyên lý hoạt động tổng quát của mô hình..."
        )

        st.markdown("**Ảnh sơ đồ mô hình tùy chỉnh (Tùy chọn - dùng để khoanh vùng ký hiệu bằng tay)**")
        diag_col1, diag_col2 = st.columns([1.3, 1])
        with diag_col1:
            uploaded_diagram_file = st.file_uploader(
                "Tải ảnh sơ đồ (.png, .jpg, .jpeg, .webp)",
                type=["png", "jpg", "jpeg", "webp"]
            )
        with diag_col2:
            existing_url = (
                edit_model.get("diagram_image", "")
                if (is_edit and edit_model.get("diagram_image", "").startswith("http"))
                else ""
            )
            diagram_image_url = st.text_input("Hoặc nhập URL ảnh sơ đồ", value=existing_url)

        st.markdown("**Danh sách Thiết bị / Khái niệm trên mô hình (*)**")
        st.caption(
            "Mỗi dòng 1 mục theo cú pháp: `Ký hiệu | Tên thiết bị | Khái niệm | Nội dung chi tiết` "
            "(Nhập `-` hoặc để trống cột Ký hiệu nếu khái niệm không có ký hiệu trên hình, ví dụ: Vòng)."
        )
        devices_raw = st.text_area("Thiết bị (*)", value=default_devices_txt, height=150)

        submitted = st.form_submit_button("💾 Lưu dữ liệu", type="primary", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Lỗi: Tên mô hình không được để trống!")
                return
            if not symbol.strip():
                st.error("Lỗi: Ký hiệu mô hình không được để trống!")
                return
            if not category.strip():
                st.error("Lỗi: Danh mục không được để trống!")
                return
            if not concept.strip():
                st.error("Lỗi: Khái niệm mô hình không được để trống!")
                return

            existing_devs = edit_model.get("devices", []) if is_edit else []
            parsed_devices, err_msg = parse_devices_text(devices_raw, existing_devs)
            if err_msg:
                st.error(f"Lỗi dữ liệu thiết bị: {err_msg}")
                return

            # Xử lý ảnh sơ đồ nếu người dùng tải lên hoặc nhập URL
            final_diagram_image = edit_model.get("diagram_image", "") if is_edit else ""
            if uploaded_diagram_file is not None:
                mime_type = uploaded_diagram_file.type or "image/png"
                b64_diag = base64.b64encode(uploaded_diagram_file.getvalue()).decode("utf-8")
                final_diagram_image = f"data:{mime_type};base64,{b64_diag}"
            elif diagram_image_url.strip():
                final_diagram_image = diagram_image_url.strip()

            if is_edit:
                for item in st.session_state.models_data:
                    if item["id"] == edit_model["id"]:
                        item["title"] = title.strip()
                        item["symbol"] = symbol.strip()
                        item["category"] = category.strip()
                        item["status"] = status
                        item["concept"] = concept.strip()
                        item["devices"] = parsed_devices
                        item["diagram_image"] = final_diagram_image
                        item.setdefault("hotspots", [])
                        break
                save_data(st.session_state.models_data)
                st.toast("Đã cập nhật mô hình thành công!", icon="✅")
            else:
                new_model = {
                    "id": str(uuid.uuid4()),
                    "title": title.strip(),
                    "category": category.strip(),
                    "created_at": datetime.now().isoformat(),
                    "status": status,
                    "symbol": symbol.strip(),
                    "diagram_image": final_diagram_image,
                    "hotspots": [],
                    "concept": concept.strip(),
                    "devices": parsed_devices
                }
                st.session_state.models_data.insert(0, new_model)
                save_data(st.session_state.models_data)
                st.toast("Đã thêm mô hình mới thành công!", icon="🎉")

            try:
                st.rerun(scope="app")
            except TypeError:
                st.rerun()


# ==========================================
# 6. FRAGMENT TƯƠNG TÁC ĐỘC LẬP (PERFORMANCE)
# ==========================================
@st.fragment
def render_models_workspace(search_name: str, search_concept: str, search_symbol: str, status_filter: str):
    """
    Fragment hiển thị danh sách thẻ [Mô hình, Thiết bị] để tối ưu hóa hiệu năng,
    tránh tải lại toàn bộ trang khi thao tác trên danh sách.
    """
    # Đồng bộ chuyển trang ngay nếu người dùng vừa chọn ký hiệu thiết bị trong Modal
    if st.session_state.current_view == "device_detail":
        try:
            st.rerun(scope="app")
        except TypeError:
            st.rerun()

    models = st.session_state.models_data

    # Empty State khi dữ liệu gốc trống
    if not models:
        st.info("Chưa có dữ liệu, hãy tạo mục đầu tiên", icon="ℹ️")
        return

    # Lọc dữ liệu theo [Tên, Khái niệm, Ký hiệu] và trạng thái
    filtered_models = []
    for m in models:
        all_names = m.get("title", "") + " " + " ".join(d.get("name", "") for d in m.get("devices", []))
        all_concepts = m.get("concept", "") + " " + " ".join(d.get("concept", "") for d in m.get("devices", []))
        all_symbols = m.get("symbol", "") + " " + " ".join(d.get("symbol", "") for d in m.get("devices", []))

        match_name = search_name.lower() in all_names.lower() if search_name else True
        match_concept = search_concept.lower() in all_concepts.lower() if search_concept else True
        match_symbol = search_symbol.lower() in all_symbols.lower() if search_symbol else True
        match_status = (m.get("status") == status_filter) if status_filter != "Tất cả" else True

        if match_name and match_concept and match_symbol and match_status:
            filtered_models.append(m)

    if not filtered_models:
        st.warning("Không tìm thấy Mô hình hoặc Thiết bị nào khớp với bộ lọc hiện tại.", icon="🔍")
        return

    # Hiển thị dưới dạng lưới thẻ (2 cột) sử dụng st.columns và st.container(border=True)
    cols = st.columns(2)
    for idx, model in enumerate(filtered_models):
        with cols[idx % 2]:
            with st.container(border=True):
                header_col1, header_col2 = st.columns([4, 1])
                with header_col1:
                    st.subheader(f"⚡ {model['title']}")
                with header_col2:
                    badge = "🟢 Completed" if model["status"] == "completed" else "🟡 Pending"
                    st.caption(badge)

                st.markdown(f"**Ký hiệu mô hình:** `{model.get('symbol', 'N/A')}` | **Phân loại:** {model['category']}")
                st.markdown(f"**Khái niệm:** {model.get('concept', '')}")

                # Thông tin [Thiết bị] trực thuộc [Mô hình]
                devices = model.get("devices", [])
                device_tags = ", ".join([
                    f"`{d['symbol']}` ({d['name']})" if d.get("symbol") else f"*{d['name']} (không ký hiệu)*"
                    for d in devices
                ])
                st.markdown(f"**Thiết bị & Khái niệm ({len(devices)}):** {device_tags if device_tags else 'Chưa có'}")

                st.divider()
                btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.8, 1.3, 0.9, 0.9])
                with btn_col1:
                    if st.button(
                        "🔍 Mở Thẻ Mô hình",
                        key=f"open_card_{model['id']}",
                        type="primary",
                        use_container_width=True
                    ):
                        open_model_modal(model)
                with btn_col2:
                    if st.button(
                        "🎯 Khoanh vùng",
                        key=f"hotspot_{model['id']}",
                        help="Tải ảnh sơ đồ & kéo chuột khoanh vùng đánh dấu ký hiệu bằng tay",
                        use_container_width=True
                    ):
                        open_hotspot_editor_modal(model)
                with btn_col3:
                    if st.button("✏️ Sửa", key=f"edit_{model['id']}", use_container_width=True):
                        open_crud_modal(model)
                with btn_col4:
                    if st.button("🗑️ Xóa", key=f"del_{model['id']}", use_container_width=True):
                        st.session_state.models_data = [
                            item for item in st.session_state.models_data if item["id"] != model["id"]
                        ]
                        save_data(st.session_state.models_data)
                        st.toast("Đã xóa mô hình thành công!", icon="🗑️")
                        try:
                            st.rerun(scope="app")
                        except TypeError:
                            st.rerun()


# ==========================================
# 7. TRANG CHI TIẾT THIẾT BỊ & HÌNH ẢNH THỰC TẾ (DEVICE DETAIL VIEW)
# ==========================================
def sync_device_images_to_storage(model_id: str, device_id: str, updated_images: list) -> None:
    """Lưu danh sách hình ảnh thực tế kèm chú thích của thiết bị vào st.session_state và data.json."""
    for model in st.session_state.models_data:
        if model["id"] == model_id:
            for dev in model.get("devices", []):
                if dev["device_id"] == device_id:
                    dev["real_images"] = updated_images
                    st.session_state.selected_device = dev
                    break
            break
    save_data(st.session_state.models_data)


def render_device_detail_page():
    """
    Trang hiển thị nội dung chi tiết của thiết bị sau khi người dùng nhấn chuột trái vào 'Ký hiệu thiết bị',
    kèm chức năng thêm và trưng bày Hình ảnh thực tế của thiết bị có chú thích.
    """
    dev = st.session_state.selected_device
    model_id = st.session_state.selected_model_id
    parent_model = next((m for m in st.session_state.models_data if m["id"] == model_id), None)

    # Đồng bộ lại dev mới nhất từ parent_model
    if parent_model and dev:
        latest_dev = next((d for d in parent_model.get("devices", []) if d["device_id"] == dev.get("device_id")), None)
        if latest_dev:
            dev = latest_dev
            st.session_state.selected_device = latest_dev

    if st.button("⬅️ Quay lại Màn hình chính", type="secondary"):
        st.session_state.current_view = "main"
        st.session_state.selected_device = None
        st.rerun()

    if not dev:
        st.error("Không tìm thấy dữ liệu thiết bị.")
        return

    st.markdown(
        f"""
        <div class="tech-hero-banner">
            <div>
                <span class="tech-badge">⚡ CHI TIẾT PHẦN TỬ / THIẾT BỊ TRÊN MÔ HÌNH</span>
                <h2 style="margin:6px 0 2px 0;">🔧 {dev['name']}</h2>
                <span style="color:#94a3b8;font-size:14px;">
                    Thuộc mô hình: <b>{parent_model['title'] if parent_model else 'N/A'}</b>
                    (<code>{parent_model.get('symbol', '') if parent_model else ''}</code>)
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_main, col_side = st.columns([2, 1])
    with col_main:
        with st.container(border=True):
            st.subheader("📖 Khái niệm & Nguyên lý")
            st.write(dev.get("concept", "Chưa có mô tả khái niệm."))

            st.divider()
            st.subheader("⚙️ Ví dụ & Nội dung chi tiết")
            st.write(dev.get("details", "Chưa có thông tin chi tiết."))

    with col_side:
        with st.container(border=True):
            st.subheader("🏷️ Định danh trên Sơ đồ")
            sym_val = dev.get("symbol", "").strip()
            st.metric(label="Ký hiệu trên sơ đồ", value=sym_val if sym_val else "Không có ký hiệu")
            st.markdown(f"**Mã định danh (ID):** `{dev.get('device_id', 'N/A')}`")
            if parent_model:
                st.markdown(f"**Danh mục:** {parent_model.get('category', 'N/A')}")
                st.divider()
                if st.button("🔍 Mở lại Sơ đồ Mô hình", type="primary", use_container_width=True):
                    open_model_modal(parent_model)

    st.divider()

    # ==========================================
    # PHẦN HÌNH ẢNH THỰC TẾ CỦA THIẾT BỊ KÈM CHÚ THÍCH
    # ==========================================
    st.subheader("📸 Hình ảnh thực tế của thiết bị & Chú thích")
    img_col_gallery, img_col_form = st.columns([1.6, 1])

    real_images = dev.get("real_images", [])

    with img_col_form:
        with st.container(border=True):
            st.markdown("##### ➕ Thêm hình ảnh thực tế mới")
            with st.form(key=f"add_real_img_form_{dev['device_id']}", clear_on_submit=True):
                uploaded_file = st.file_uploader(
                    "Tải ảnh thực tế từ máy tính (.png, .jpg, .jpeg, .webp)",
                    type=["png", "jpg", "jpeg", "webp"]
                )
                image_url = st.text_input(
                    "Hoặc dán đường dẫn URL hình ảnh",
                    placeholder="https://example.com/device.jpg"
                )
                caption = st.text_area(
                    "Chú thích hình ảnh thực tế (*)",
                    placeholder="VD: Hình thực tế Pin 9V và Ắc quy chì 12V sử dụng trong phòng thí nghiệm...",
                    height=90
                )
                submit_img = st.form_submit_button("📸 Lưu hình ảnh & Chú thích", type="primary", use_container_width=True)

                if submit_img:
                    if not uploaded_file and not image_url.strip():
                        st.error("Lỗi: Vui lòng tải lên 1 file ảnh hoặc nhập đường dẫn URL hình ảnh!")
                    elif not caption.strip():
                        st.error("Lỗi: Vui lòng nhập chú thích cho hình ảnh thực tế!")
                    else:
                        if uploaded_file is not None:
                            mime_type = uploaded_file.type or "image/png"
                            b64_encoded = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                            final_img_src = f"data:{mime_type};base64,{b64_encoded}"
                        else:
                            final_img_src = image_url.strip()

                        new_img_entry = {
                            "image_id": f"img-{uuid.uuid4().hex[:8]}",
                            "image_data": final_img_src,
                            "caption": caption.strip(),
                            "created_at": datetime.now().isoformat()
                        }
                        updated_list = list(real_images) + [new_img_entry]
                        sync_device_images_to_storage(model_id, dev["device_id"], updated_list)
                        st.toast("Đã thêm hình ảnh thực tế kèm chú thích thành công!", icon="📸")
                        st.rerun()

    with img_col_gallery:
        if not real_images:
            with st.container(border=True):
                st.info(
                    "Chưa có hình ảnh thực tế nào cho thiết bị này. "
                    "Hãy tải ảnh lên kèm chú thích ở khung bên phải để trực quan hóa bài học!",
                    icon="🖼️"
                )
        else:
            gallery_cols = st.columns(2)
            for idx, img_item in enumerate(real_images):
                with gallery_cols[idx % 2]:
                    with st.container(border=True):
                        st.image(img_item["image_data"], use_container_width=True)
                        st.markdown(f"**📝 Chú thích:** {img_item.get('caption', '')}")
                        if st.button(
                            "🗑️ Xóa ảnh",
                            key=f"del_img_{dev['device_id']}_{img_item['image_id']}",
                            use_container_width=True
                        ):
                            remaining_imgs = [
                                item for item in real_images if item["image_id"] != img_item["image_id"]
                            ]
                            sync_device_images_to_storage(model_id, dev["device_id"], remaining_imgs)
                            st.toast("Đã xóa hình ảnh thực tế!", icon="🗑️")
                            st.rerun()


# ==========================================
# 8. ĐIỀU HƯỚNG, ĐỒNG BỘ GITHUB, SAO LƯU JSON & BỐ CỤC CHÍNH
# ==========================================
def render_sidebar_export_import() -> None:
    """Hiển thị trạng thái đồng bộ GitHub Cloud và công cụ Xuất (Export) / Nhập (Import) data.json trên Sidebar."""
    st.subheader("☁️ Đồng bộ Đám mây (GitHub)")
    gh_cfg = get_github_config()

    if gh_cfg["enabled"]:
        st.caption(f"🟢 **GitHub Auto-Sync:** `{gh_cfg['repo']}` (`{gh_cfg['branch']}`)")
        if st.button("🔄 Tải dữ liệu mới nhất từ GitHub", use_container_width=True):
            pulled = github_pull_data()
            if isinstance(pulled, list):
                st.session_state.models_data = _normalize_loaded_models(pulled)
                st.toast("Đã đồng bộ dữ liệu mới nhất từ GitHub!", icon="☁️")
                st.rerun()
            else:
                st.error("Không thể tải dữ liệu từ GitHub. Vui lòng kiểm tra Token hoặc tên Repo.")
    else:
        st.caption("⚪ **Trạng thái:** Lưu nội bộ (`data.json`)")
        with st.expander("⚙️ Kết nối GitHub Auto-Sync", expanded=False):
            st.caption("Nhập thông tin dưới đây hoặc cấu hình trong `st.secrets` trên Streamlit Cloud:")
            in_repo = st.text_input("GitHub Repo (VD: ten-ban/model-ddt)", key="ui_gh_repo")
            in_token = st.text_input("GitHub Personal Access Token", type="password", key="ui_gh_token")
            in_branch = st.text_input("Nhánh (Branch)", value="main", key="ui_gh_branch")
            if st.button("🔗 Kết nối & Đồng bộ ngay", type="primary", use_container_width=True):
                if in_repo.strip() and in_token.strip():
                    st.session_state.custom_github_config = {
                        "repo": in_repo.strip(),
                        "token": in_token.strip(),
                        "branch": in_branch.strip() or "main"
                    }
                    ok, msg = github_push_data(st.session_state.models_data, "Initial sync from Model DDT")
                    if ok:
                        st.toast("Đã kết nối và đẩy dữ liệu lên GitHub thành công!", icon="✅")
                        st.rerun()
                    else:
                        st.error(f"Kết nối thất bại: {msg}")
                else:
                    st.error("Vui lòng nhập đủ GitHub Repo và Token!")

    st.divider()
    st.subheader("📦 Sao lưu & Chia sẻ (JSON)")

    json_bytes = json.dumps(st.session_state.models_data, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        label="📤 Xuất (Export) data.json",
        data=json_bytes,
        file_name="data.json",
        mime="application/json",
        use_container_width=True,
        help="Tải toàn bộ dữ liệu mô hình, vùng khoanh ký hiệu và hình ảnh thực tế về máy dưới dạng file data.json"
    )

    uploaded_json = st.file_uploader(
        "📥 Nhập (Import) file data.json",
        type=["json"],
        key="sidebar_import_json_uploader",
        help="Chọn file data.json từ máy tính để khôi phục hoặc nạp bộ dữ liệu học phần mới"
    )
    if uploaded_json is not None:
        if st.button("🔄 Nạp dữ liệu từ file JSON", type="primary", use_container_width=True):
            try:
                raw_content = json.loads(uploaded_json.getvalue().decode("utf-8"))
                normalized_data, err_msg = validate_and_normalize_models_json(raw_content)
                if err_msg:
                    st.error(f"Lỗi cấu trúc JSON: {err_msg}")
                else:
                    st.session_state.models_data = normalized_data
                    save_data(normalized_data)
                    st.toast(f"Đã nhập thành công {len(normalized_data)} mô hình từ file data.json!", icon="📥")
                    st.rerun()
            except (UnicodeDecodeError, json.JSONDecodeError):
                st.error("Lỗi: File tải lên không phải là định dạng JSON hợp lệ!")


def main():
    # Sidebar: Bộ lọc và Tìm kiếm theo [Tên, Khái niệm, Ký hiệu] + GitHub Sync & Export/Import data.json
    with st.sidebar:
        st.header("🎛️ Công cụ & Bộ lọc ĐĐT")
        if st.button("➕ Tạo Mô hình mới", type="primary", use_container_width=True):
            open_crud_modal(None)

        st.divider()
        st.subheader("🔎 Tìm kiếm & Lọc")
        search_name = st.text_input("Tìm theo Tên (Mô hình / Thiết bị)", placeholder="VD: Nguồn, Tải, Nhánh, Nút, Vòng...")
        search_concept = st.text_input("Tìm theo Khái niệm", placeholder="VD: mạch kín, giao điểm, điện năng...")
        search_symbol = st.text_input("Tìm theo Ký hiệu", placeholder="VD: E1, R1, Nút A, Dây dẫn...")
        status_filter = st.selectbox("Lọc theo Trạng thái", options=["Tất cả", "completed", "pending"])

        st.divider()
        render_sidebar_export_import()

        st.divider()
        st.caption(f"Tổng số mô hình hiện có: **{len(st.session_state.models_data)}**")

    # Điều hướng giữa Màn hình chính và Trang chi tiết thiết bị
    if st.session_state.current_view == "device_detail":
        render_device_detail_page()
    else:
        st.markdown(
            """
            <div class="tech-hero-banner">
                <div>
                    <span class="tech-badge">⚡ HỆ THỐNG MÔ PHỎNG & TRỰC QUAN HÓA SƠ ĐỒ MẠCH ĐIỆN</span>
                    <h1 style="margin:6px 0 4px 0; font-size:28px;">Model ĐĐT — Kỹ thuật Điện - Điện tử</h1>
                    <span style="color:#94a3b8; font-size:14.5px;">
                        Chọn <b>Thẻ mô hình</b> để mở bản vẽ kỹ thuật tương tác (<b>Hình 1.1</b> & <b>Hình 1.2</b>),
                        hoặc dùng <b>🎯 Khoanh vùng</b> để tải ảnh sơ đồ mới và kéo chuột đánh dấu ký hiệu bằng tay.
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        render_models_workspace(search_name, search_concept, search_symbol, status_filter)


if __name__ == "__main__":
    main()