import base64
import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid
import webbrowser
from datetime import datetime


# ==========================================
# 0. BOOTSTRAPPER: TỰ ĐỘNG CÀI ĐẶT FLASK & MỞ TRÌNH DUYỆT
# ==========================================
def _ensure_flask_installed() -> None:
    """Kiểm tra và tự động cài đặt thư viện Flask vào đúng môi trường Python đang chạy."""
    try:
        import flask  # noqa: F401
    except ModuleNotFoundError:
        print("⚠️ Phát hiện môi trường Python hiện tại chưa có thư viện 'flask'.")
        print(f"🔧 Đang tự động cài đặt 'flask' vào: {sys.executable} ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        except Exception:
            try:
                import ensurepip
                ensurepip.bootstrap()
            except Exception:
                pass
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        print("✅ Đã cài đặt 'flask' thành công!")


_ensure_flask_installed()

from flask import Flask, Response, jsonify, render_template_string, request  # noqa: E402

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # Cho phép tải ảnh/JSON tối đa 32MB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
CONFIG_FILE = os.path.join(BASE_DIR, "github_sync_config.json")

# ==========================================
# 1. QUẢN LÝ DỮ LIỆU & LƯU TRỮ (DATA LAYER)
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
    },
    {
        "id": "model-hinh-1-3",
        "title": "Hình 1.3: Dòng điện và điện áp",
        "category": "1.2. Các đại lượng đặc trưng cho quá trình năng lượng điện",
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "symbol": "H1.3",
        "diagram_type": "fig_1_3",
        "diagram_image": "",
        "hotspots": [],
        "concept": (
            "Biểu diễn các đại lượng đặc trưng cho quá trình năng lượng điện trên một nhánh mạch (a - b) "
            "bao gồm: dòng điện i chạy qua phần tử, điện áp u_ab giữa hai đầu nhánh và công suất tức thời p(t)."
        ),
        "devices": [
            {
                "device_id": "h13-dongdien",
                "symbol": "i",
                "name": "Dòng điện (i)",
                "concept": (
                    "Dòng điện i về trị số bằng tốc độ biến thiên của lượng điện tích q qua tiết diện ngang một vật dẫn:\n"
                    "Công thức: i = dq / dt   (1.1)"
                ),
                "details": (
                    "- Chiều dòng điện quy ước là chiều chuyển động của các điện tích dương (ion dương), "
                    "ngược với chiều chuyển động của các ion âm hoặc electron (điện tử).\n"
                    "- Trên một nhánh, chiều dương quy ước của dòng điện được chọn tùy ý và ký hiệu bằng mũi tên.\n"
                    "- Đơn vị đo của dòng điện là Ampe. Ký hiệu là A."
                ),
                "real_images": []
            },
            {
                "device_id": "h13-dienap",
                "symbol": "u_ab",
                "name": "Điện áp (u_ab)",
                "concept": (
                    "Tại mỗi điểm trong mạch điện có một điện thế. Hiệu điện thế (hiệu thế) giữa hai điểm gọi là điện áp. "
                    "Như vậy điện áp giữa hai điểm a và b có điện thế φ_a, φ_b là:\n"
                    "Công thức: u_ab = φ_a - φ_b   (1.2)"
                ),
                "details": (
                    "- Chiều điện áp quy ước là chiều từ điểm có điện thế cao đến điểm có điện thế thấp.\n"
                    "- Điện áp giữa hai cực của nguồn điện khi hở mạch ngoài (dòng điện I = 0) được gọi là suất điện động E.\n"
                    "- Đơn vị đo của điện áp, suất điện động là Volt. Ký hiệu là V."
                ),
                "real_images": []
            },
            {
                "device_id": "h13-congsuat",
                "symbol": "",
                "name": "Công suất tức thời p(t)",
                "concept": (
                    "Công suất tức thời của nhánh tại thời điểm t được xác định bằng tích của điện áp tức thời và dòng điện tức thời:\n"
                    "Công thức: p(t) = u(t) . i(t)   (1.3)"
                ),
                "details": (
                    "Khi chọn chiều dòng điện và điện áp trên nhánh trùng nhau, sau khi tính toán công suất p của nhánh, "
                    "tại một thời điểm nào đó, dựa vào dấu của p ta có kết luận sau về quá trình năng lượng của nhánh:\n"
                    "- p = u.i > 0 : nhánh nhận năng lượng.\n"
                    "- p = u.i < 0 : nhánh phát năng lượng.\n"
                    "- Đơn vị đo của công suất là W (Oát) hoặc kW."
                ),
                "real_images": []
            }
        ]
    },
    {
        "id": "model-hinh-1-4",
        "title": "Hình 1.4: Ký hiệu của điện trở",
        "category": "1.3. Các phần tử cơ bản của mạch điện - 1.3.1. Điện trở",
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "symbol": "H1.4",
        "diagram_type": "fig_1_4",
        "diagram_image": "",
        "hotspots": [],
        "concept": (
            "Điện trở là linh kiện điện tử thụ động trong mạch điện, có chức năng cản trở (hạn chế) dòng điện đi qua nó "
            "và chuyển đổi điện năng thành nhiệt năng. Ký hiệu: R — Đơn vị: Ω (Ohm)."
        ),
        "devices": [
            {
                "device_id": "h14-dientro",
                "symbol": "R",
                "name": "Điện trở (R) & Hướng dẫn đọc trị số vòng màu",
                "concept": (
                    "Điện trở là linh kiện điện tử thụ động trong mạch điện, nó có chức năng là cản trở (hạn chế) dòng điện "
                    "đi qua nó, nó có thể chuyển đổi điện năng thành nhiệt năng.\n"
                    "- Ký hiệu: R\n"
                    "- Đơn vị: Ω (Ohm)"
                ),
                "details": (
                    "Cách đọc trị số của điện trở theo quy ước vòng màu:\n"
                    "- Thường được ký hiệu bằng 4 vòng màu. Ngoài ra còn có loại 5 vòng màu và 3 vòng màu.\n"
                    "- Điện trở 4 vòng màu: Vòng số 1 và số 2 là vòng chục và vòng đơn vị; Vòng số 3 là bội số cơ số 10; Vòng số 4 là sai số của điện trở. Công thức: Trị số = (vòng 1)(vòng 2) x 10^(vòng 3).\n"
                    "- Điện trở 5 vòng màu: Vòng 1, 2, 3 là 3 chữ số có nghĩa; Vòng 4 là bội số cơ số 10; Vòng 5 là sai số. Công thức: Trị số = (vòng 1)(vòng 2)(vòng 3) x 10^(vòng 4).\n"
                    "- Ghi chú: Vòng màu sai số Không màu (điện trở 3 vòng màu) – mặc định là ± 20%."
                ),
                "real_images": []
            }
        ]
    },
    {
        "id": "model-hinh-1-7",
        "title": "Hình 1.7: Ký hiệu của cuộn dây",
        "category": "1.3. Các phần tử cơ bản của mạch điện - 1.3.2. Cuộn dây",
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "symbol": "H1.7",
        "diagram_type": "fig_1_7",
        "diagram_image": "",
        "hotspots": [],
        "concept": (
            "Cuộn cảm (Inductor) còn được gọi là cuộn dây (coil, choke) là linh kiện điện tử thụ động dùng để lưu trữ "
            "năng lượng dưới dạng từ trường khi có dòng điện chạy qua. Ký hiệu: L — Đơn vị: H (Henry), 1 mH = 10^-3 H."
        ),
        "devices": [
            {
                "device_id": "h17-cuonday",
                "symbol": "L",
                "name": "Cuộn dây / Cuộn cảm (L) & Hướng dẫn đọc trị số điện cảm",
                "concept": (
                    "Cuộn cảm (Inductor) còn được gọi là cuộn dây (coil, choke) là linh kiện điện tử thụ động dùng để "
                    "lưu trữ năng lượng dưới dạng từ trường khi có dòng điện chạy qua.\n"
                    "- Ký hiệu: L\n"
                    "- Đơn vị: H (Henry) (1 mH = 10^-3 H)"
                ),
                "details": (
                    "Tính chất của cuộn dây:\n"
                    "- i là dòng điện đi qua cuộn dây\n"
                    "- u_L là điện áp đặt giữa 2 đầu cuộn dây: u_L = L . (di / dt)   (1.4)\n"
                    "- di/dt: chỉ sự biến thiên của dòng điện theo thời gian.\n"
                    "- Điện áp giữa 2 đầu cuộn dây tỉ lệ với sự biến thiên của dòng điện theo thời gian."
                ),
                "real_images": []
            }
        ]
    }
]


def get_github_config() -> dict:
    """Đọc cấu hình GitHub Auto-Sync từ biến môi trường hoặc file cấu hình nội bộ."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPO", "").strip()
    branch = os.environ.get("GITHUB_BRANCH", "main").strip() or "main"
    file_path = os.environ.get("GITHUB_FILE_PATH", "data.json").strip() or "data.json"

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if cfg.get("token") and cfg.get("repo"):
                token = cfg["token"].strip()
                repo = cfg["repo"].strip()
                branch = cfg.get("branch", "main").strip() or "main"
        except Exception:
            pass

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


def github_pull_data():
    """Tải nội dung data.json từ GitHub REST API (nếu có cấu hình)."""
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
            "User-Agent": "Model-DDT-Flask-App"
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


def github_push_data(data: list, commit_msg: str = "Auto-sync data.json from Model DDT Web App") -> tuple:
    """Đẩy (Commit & Push) data.json lên GitHub qua REST API."""
    cfg = get_github_config()
    if not cfg["enabled"]:
        return False, "Chưa cấu hình GitHub Token/Repo."

    base_url = f"https://api.github.com/repos/{cfg['repo']}/contents/{cfg['path']}"
    headers = {
        "Authorization": f"Bearer {cfg['token']}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "Model-DDT-Flask-App"
    }

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
    """Đảm bảo mọi mô hình và thiết bị đều có đủ trường diagram_image, hotspots, real_images."""
    for model in data:
        if "diagram_image" not in model or not isinstance(model["diagram_image"], str):
            model["diagram_image"] = ""
        if "hotspots" not in model or not isinstance(model["hotspots"], list):
            model["hotspots"] = []
        for dev in model.get("devices", []):
            if "real_images" not in dev or not isinstance(dev["real_images"], list):
                dev["real_images"] = []
    return data


def _merge_missing_default_models(data: list) -> tuple:
    """Bổ sung các mô hình mặc định mới (Hình 1.3, 1.4, 1.7) nếu file data.json cũ chưa có."""
    existing_ids = {item.get("id") for item in data if isinstance(item, dict)}
    changed = False
    for default_item in DEFAULT_DATA:
        if default_item["id"] not in existing_ids:
            data.append(json.loads(json.dumps(default_item)))
            changed = True
    return data, changed


def load_data() -> list:
    """Đọc dữ liệu từ file data.json (hoặc từ GitHub nếu mới khởi tạo)."""
    if not os.path.exists(DATA_FILE):
        remote_data = github_pull_data()
        if isinstance(remote_data, list) and remote_data:
            normalized_remote = _normalize_loaded_models(remote_data)
            normalized_remote, _ = _merge_missing_default_models(normalized_remote)
            save_data(normalized_remote)
            return normalized_remote
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        old_symbols = {"DOL-3P", "AC-DC-7812"}
        if data and all(item.get("symbol") in old_symbols for item in data):
            save_data(DEFAULT_DATA)
            return DEFAULT_DATA
        data = _normalize_loaded_models(data)
        data, changed = _merge_missing_default_models(data)
        if changed:
            save_data(data)
        return data
    except (json.JSONDecodeError, IOError):
        return []


def save_data(data: list) -> None:
    """Ghi đè dữ liệu bền vững xuống file data.json trên ổ cứng máy chủ và đồng bộ GitHub (nếu bật)."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    cfg = get_github_config()
    if cfg["enabled"]:
        github_push_data(data)


# ==========================================
# 2. VALIDATION & CRUD HELPERS (HỖ TRỢ KHÁI NIỆM & CHI TIẾT NHIỀU DÒNG)
# ==========================================
def parse_devices_text(raw_text: str, existing_devices: list = None) -> tuple:
    """
    Phân tích chuỗi nhập thiết bị theo định dạng:
    Ký hiệu | Tên thiết bị | Khái niệm | Nội dung chi tiết
    Hỗ trợ nội dung nhiều dòng (xuống dòng trực tiếp hoặc ký tự \\n):
    - Dòng có đủ 4 phần ngăn cách bởi dấu '|' sẽ bắt đầu một thiết bị/khái niệm mới.
    - Các dòng tiếp theo không chứa đủ 3 dấu '|' sẽ được nối thêm bằng dấu xuống dòng ('\n')
      vào thiết bị liền trước (hoặc nếu có 1 dấu '|' thì phần trước nối vào Khái niệm, phần sau nối vào Chi tiết).
    """
    existing_devices = existing_devices or []
    existing_by_key = {}
    for ed in existing_devices:
        key_pair = (ed.get("symbol", "").strip(), ed.get("name", "").strip())
        existing_by_key[key_pair] = ed
        existing_by_key[ed.get("name", "").strip()] = ed

    raw_lines = (raw_text or "").replace("\r\n", "\n").split("\n")
    parsed_records = []

    for idx, line in enumerate(raw_lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            raw_symbol = parts[0]
            name = parts[1]
            concept = parts[2].replace("\\n", "\n")
            details = "|".join(parts[3:]).strip().replace("\\n", "\n")
            parsed_records.append({
                "line_no": idx,
                "raw_symbol": raw_symbol,
                "name": name,
                "concept": concept,
                "details": details
            })
        else:
            if parsed_records:
                if len(parts) == 2:
                    if parts[0]:
                        parsed_records[-1]["concept"] += "\n" + parts[0].replace("\\n", "\n")
                    if parts[1]:
                        parsed_records[-1]["details"] += "\n" + parts[1].replace("\\n", "\n")
                else:
                    parsed_records[-1]["details"] += "\n" + stripped.replace("\\n", "\n")
            else:
                return [], (
                    f"Dòng thứ {idx} thiếu trường thông tin. "
                    "Vui lòng nhập đủ 4 phần: Ký hiệu (hoặc '-' nếu không có) | Tên thiết bị | Khái niệm | Nội dung chi tiết"
                )

    if not parsed_records:
        return [], "Mô hình phải có ít nhất 1 thiết bị hoặc khái niệm."

    devices = []
    for idx, rec in enumerate(parsed_records, start=1):
        raw_symbol = rec["raw_symbol"]
        name = rec["name"]
        concept = rec["concept"].strip()
        details = rec["details"].strip()
        if not name or not concept or not details:
            return [], (
                f"Mục thiết bị thứ {idx}: Tên thiết bị, Khái niệm và Nội dung chi tiết không được để trống."
            )
        normalized_symbol = "" if raw_symbol == "-" else raw_symbol

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


def parse_devices_input(devices_payload, raw_text: str = "", existing_devices: list = None) -> tuple:
    """
    Xử lý danh sách thiết bị/khái niệm gửi từ form CRUD:
    - Ưu tiên nhận mảng đối tượng `devices_payload` (hỗ trợ nhập nhiều dòng trực tiếp cho từng Khái niệm và Chi tiết).
    - Nếu không có mảng `devices_payload`, tự động chuyển sang phân tích `raw_text` qua `parse_devices_text`.
    """
    existing_devices = existing_devices or []
    if isinstance(devices_payload, list) and len(devices_payload) > 0:
        existing_by_id = {ed.get("device_id"): ed for ed in existing_devices if ed.get("device_id")}
        existing_by_key = {}
        for ed in existing_devices:
            key_pair = (ed.get("symbol", "").strip(), ed.get("name", "").strip())
            existing_by_key[key_pair] = ed
            existing_by_key[ed.get("name", "").strip()] = ed

        devices = []
        for idx, item in enumerate(devices_payload, start=1):
            if not isinstance(item, dict):
                continue
            raw_symbol = (item.get("symbol") or "").strip()
            name = (item.get("name") or "").strip()
            concept = (item.get("concept") or "").replace("\r\n", "\n").strip()
            details = (item.get("details") or "").replace("\r\n", "\n").strip()

            if not name and not concept and not details and not raw_symbol:
                continue
            if not name or not concept or not details:
                return [], (
                    f"Thiết bị / Khái niệm thứ {idx}: Vui lòng nhập đầy đủ Tên thiết bị, Khái niệm và Nội dung chi tiết!"
                )
            normalized_symbol = "" if raw_symbol == "-" else raw_symbol
            provided_id = (item.get("device_id") or "").strip()

            matched_old = (
                existing_by_id.get(provided_id)
                or existing_by_key.get((normalized_symbol, name))
                or existing_by_key.get(name)
                or (existing_devices[idx - 1] if idx - 1 < len(existing_devices) else None)
            )
            dev_id = (
                provided_id
                or (matched_old["device_id"] if matched_old and "device_id" in matched_old else f"dev-{uuid.uuid4().hex[:8]}")
            )
            real_imgs = matched_old.get("real_images", []) if matched_old else []

            devices.append({
                "device_id": dev_id,
                "symbol": normalized_symbol,
                "name": name,
                "concept": concept,
                "details": details,
                "real_images": real_imgs
            })

        if not devices:
            return [], "Mô hình phải có ít nhất 1 thiết bị hoặc khái niệm."
        return devices, ""

    return parse_devices_text(raw_text, existing_devices)


def format_devices_to_text(devices: list) -> str:
    """Chuyển danh sách thiết bị sang chuỗi văn bản (bảo toàn ký tự xuống dòng)."""
    escaped_nl = chr(92) + "n"
    return "\n".join(
        f"{d.get('symbol') if d.get('symbol') else '-'} | {d.get('name', '')} | "
        f"{d.get('concept', '').replace(chr(10), escaped_nl)} | {d.get('details', '').replace(chr(10), escaped_nl)}"
        for d in devices
    )


def validate_and_normalize_models_json(raw_data: list) -> tuple:
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


def sync_model_diagram_and_hotspots(model_id: str, diagram_image: str = None, hotspots: list = None) -> list:
    """Cập nhật ảnh sơ đồ mô hình (diagram_image) và danh sách vùng đánh dấu (hotspots) vào data.json."""
    data = load_data()
    for item in data:
        if item["id"] == model_id:
            if diagram_image is not None:
                item["diagram_image"] = diagram_image
            if hotspots is not None:
                item["hotspots"] = hotspots
            break
    save_data(data)
    return data


def sync_device_images_to_storage(model_id: str, device_id: str, updated_images: list) -> list:
    """Lưu danh sách hình ảnh thực tế kèm chú thích của thiết bị vào data.json."""
    data = load_data()
    for model in data:
        if model["id"] == model_id:
            for dev in model.get("devices", []):
                if dev["device_id"] == device_id:
                    dev["real_images"] = updated_images
                    break
            break
    save_data(data)
    return data


# ==========================================
# 3. FLASK REST API ENDPOINTS
# ==========================================
@app.route("/api/models", methods=["GET"])
def api_get_models():
    data = load_data()
    gh_cfg = get_github_config()
    return jsonify({
        "ok": True,
        "models": data,
        "github": {
            "enabled": gh_cfg["enabled"],
            "repo": gh_cfg["repo"],
            "branch": gh_cfg["branch"]
        }
    })


@app.route("/api/models", methods=["POST"])
def api_save_model():
    payload = request.get_json(force=True, silent=True) or {}
    edit_id = (payload.get("id") or "").strip()
    title = (payload.get("title") or "").strip()
    symbol = (payload.get("symbol") or "").strip()
    category = (payload.get("category") or "").strip()
    status = (payload.get("status") or "completed").strip()
    concept = (payload.get("concept") or "").replace("\r\n", "\n").strip()
    devices_list = payload.get("devices")
    devices_raw = (payload.get("devices_raw") or "").strip()
    diagram_image = payload.get("diagram_image")

    if not title:
        return jsonify({"ok": False, "error": "Lỗi: Tên mô hình không được để trống!"}), 400
    if not symbol:
        return jsonify({"ok": False, "error": "Lỗi: Ký hiệu mô hình không được để trống!"}), 400
    if not category:
        return jsonify({"ok": False, "error": "Lỗi: Danh mục không được để trống!"}), 400
    if not concept:
        return jsonify({"ok": False, "error": "Lỗi: Khái niệm mô hình không được để trống!"}), 400

    data = load_data()
    existing_model = next((m for m in data if m["id"] == edit_id), None) if edit_id else None
    existing_devs = existing_model.get("devices", []) if existing_model else []

    parsed_devices, err_msg = parse_devices_input(devices_list, devices_raw, existing_devs)
    if err_msg:
        return jsonify({"ok": False, "error": f"Lỗi dữ liệu thiết bị: {err_msg}"}), 400

    if existing_model:
        existing_model["title"] = title
        existing_model["symbol"] = symbol
        existing_model["category"] = category
        existing_model["status"] = status
        existing_model["concept"] = concept
        existing_model["devices"] = parsed_devices
        if diagram_image is not None and diagram_image != "":
            existing_model["diagram_image"] = diagram_image
        existing_model.setdefault("hotspots", [])
    else:
        new_model = {
            "id": str(uuid.uuid4()),
            "title": title,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "status": status,
            "symbol": symbol,
            "diagram_image": diagram_image or "",
            "hotspots": [],
            "concept": concept,
            "devices": parsed_devices
        }
        data.insert(0, new_model)

    save_data(data)
    return jsonify({"ok": True, "models": data})


@app.route("/api/models/<model_id>", methods=["DELETE"])
def api_delete_model(model_id: str):
    data = load_data()
    data = [m for m in data if m["id"] != model_id]
    save_data(data)
    return jsonify({"ok": True, "models": data})


@app.route("/api/models/<model_id>/hotspots", methods=["POST"])
def api_update_hotspots(model_id: str):
    payload = request.get_json(force=True, silent=True) or {}
    diagram_image = payload.get("diagram_image")
    hotspots = payload.get("hotspots")
    data = sync_model_diagram_and_hotspots(model_id, diagram_image=diagram_image, hotspots=hotspots)
    return jsonify({"ok": True, "models": data})


@app.route("/api/models/<model_id>/devices/<device_id>/images", methods=["POST"])
def api_manage_device_images(model_id: str, device_id: str):
    payload = request.get_json(force=True, silent=True) or {}
    action = payload.get("action", "add")
    data = load_data()

    target_dev = None
    for m in data:
        if m["id"] == model_id:
            for d in m.get("devices", []):
                if d["device_id"] == device_id:
                    target_dev = d
                    break
            break

    if not target_dev:
        return jsonify({"ok": False, "error": "Không tìm thấy thiết bị!"}), 404

    real_images = list(target_dev.get("real_images", []))
    if action == "add":
        img_src = (payload.get("image_data") or "").strip()
        caption = (payload.get("caption") or "").strip()
        if not img_src:
            return jsonify({"ok": False, "error": "Lỗi: Vui lòng tải lên 1 file ảnh hoặc nhập đường dẫn URL hình ảnh!"}), 400
        if not caption:
            return jsonify({"ok": False, "error": "Lỗi: Vui lòng nhập chú thích cho hình ảnh thực tế!"}), 400
        real_images.append({
            "image_id": f"img-{uuid.uuid4().hex[:8]}",
            "image_data": img_src,
            "caption": caption,
            "created_at": datetime.now().isoformat()
        })
    elif action == "delete":
        image_id = payload.get("image_id", "")
        real_images = [img for img in real_images if img.get("image_id") != image_id]

    updated_data = sync_device_images_to_storage(model_id, device_id, real_images)
    return jsonify({"ok": True, "models": updated_data})


@app.route("/api/export", methods=["GET"])
def api_export_json():
    data = load_data()
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    return Response(
        json_bytes,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=data.json"}
    )


@app.route("/api/import", methods=["POST"])
def api_import_json():
    payload = request.get_json(force=True, silent=True) or {}
    raw_data = payload.get("data")
    normalized_data, err_msg = validate_and_normalize_models_json(raw_data)
    if err_msg:
        return jsonify({"ok": False, "error": f"Lỗi cấu trúc JSON: {err_msg}"}), 400
    save_data(normalized_data)
    return jsonify({"ok": True, "models": normalized_data})


@app.route("/api/github-sync", methods=["POST"])
def api_github_sync():
    payload = request.get_json(force=True, silent=True) or {}
    action = payload.get("action", "pull")
    if action == "config":
        repo = (payload.get("repo") or "").strip()
        token = (payload.get("token") or "").strip()
        branch = (payload.get("branch") or "main").strip() or "main"
        if not repo or not token:
            return jsonify({"ok": False, "error": "Vui lòng nhập đủ GitHub Repo và Token!"}), 400
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"repo": repo, "token": token, "branch": branch}, f, indent=2)
        data = load_data()
        ok, msg = github_push_data(data, "Initial sync from Model DDT Flask App")
        if not ok:
            return jsonify({"ok": False, "error": f"Kết nối thất bại: {msg}"}), 400
        return jsonify({"ok": True, "models": data, "github": get_github_config()})

    elif action == "pull":
        pulled = github_pull_data()
        if isinstance(pulled, list):
            normalized = _normalize_loaded_models(pulled)
            save_data(normalized)
            return jsonify({"ok": True, "models": normalized})
        return jsonify({"ok": False, "error": "Không thể tải dữ liệu từ GitHub. Vui lòng kiểm tra Token hoặc tên Repo."}), 400

    return jsonify({"ok": False, "error": "Hành động không hợp lệ."}), 400


# ==========================================
# 4. GIAO DIỆN WEB TƯƠNG TÁC (TECH-BROWN ESPRESSO & CYBER AMBER DASHBOARD UI + SVG HÌNH 1.1 -> 1.7 + QUIZ ĐIỆN TRỞ & ĐIỆN CẢM)
# ==========================================
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
    <title>Model ĐĐT — Kỹ thuật Điện - Điện tử</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-espresso: #0f0905;
            --bg-blueprint-warm: #160d07;
            --bg-panel: #180f08;
            --card-bg: rgba(26, 16, 9, 0.88);
            --card-bg-hover: rgba(34, 21, 12, 0.94);
            --sidebar-bg: #140c06;
            --rail-bg: #0c0704;
            --copper: #b45309;
            --copper-bright: #d97706;
            --copper-border: rgba(180, 83, 9, 0.42);
            --copper-glow: rgba(245, 158, 11, 0.25);
            --amber-cyber: #f59e0b;
            --amber-light: #fbbf24;
            --amber-pale: #fde68a;
            --cream-sand: #f3e6d0;
            --emerald-bg: rgba(6, 78, 59, 0.55);
            --emerald-border: rgba(16, 185, 129, 0.45);
            --emerald-text: #34d399;
            --text-main: #f5ebe1;
            --text-secondary: #d6c3b0;
            --text-muted: #9c846e;
            --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
            --font-display: 'Plus Jakarta Sans', 'Inter', sans-serif;
            --font-mono: 'JetBrains Mono', 'Consolas', monospace;
        }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }

        /* NỀN TECH-BROWN ESPRESSO (#0f0905) & HIỆU ỨNG LƯỚI ĐIỆN TỬ ẨN (CYBER GRID) */
        body {
            margin: 0;
            font-family: var(--font-sans);
            background-color: var(--bg-espresso);
            background-image:
                radial-gradient(circle at 22% 14%, rgba(245, 158, 11, 0.11) 0%, transparent 38%),
                radial-gradient(circle at 82% 22%, rgba(180, 83, 9, 0.14) 0%, transparent 42%),
                radial-gradient(circle at 50% 88%, rgba(180, 83, 9, 0.09) 0%, transparent 48%),
                linear-gradient(rgba(245, 158, 11, 0.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(245, 158, 11, 0.045) 1px, transparent 1px),
                linear-gradient(rgba(180, 83, 9, 0.022) 1px, transparent 1px),
                linear-gradient(90deg, rgba(180, 83, 9, 0.022) 1px, transparent 1px),
                linear-gradient(180deg, #0f0905 0%, #150c06 50%, #0d0804 100%);
            background-size:
                100% 100%, 100% 100%, 100% 100%,
                80px 80px, 80px 80px,
                16px 16px, 16px 16px,
                100% 100%;
            background-attachment: fixed;
            color: var(--text-main);
            display: flex;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* THANH ICON RAIL DỌC BÊN TRÁI (THEO MẪU DASHBOARD) */
        .icon-rail {
            width: 56px;
            min-width: 56px;
            background: var(--rail-bg);
            border-right: 1px solid rgba(180, 83, 9, 0.28);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16px 0;
            gap: 14px;
            z-index: 1060;
            position: sticky;
            top: 0;
            height: 100vh;
        }
        .rail-logo {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.22), rgba(180, 83, 9, 0.35));
            border: 1px solid var(--amber-cyber);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--amber-light);
            font-weight: 800;
            font-size: 16px;
            box-shadow: 0 0 14px rgba(245, 158, 11, 0.25);
            cursor: pointer;
            margin-bottom: 8px;
        }
        .rail-btn {
            width: 38px;
            height: 38px;
            border-radius: 9px;
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .rail-btn:hover, .rail-btn.active {
            background: rgba(180, 83, 9, 0.22);
            border-color: var(--copper-border);
            color: var(--amber-light);
            box-shadow: 0 0 12px rgba(180, 83, 9, 0.3);
        }
        .rail-spacer { flex: 1; }

        /* LỚP PHỦ MỜ KHI MỞ TASKBAR TRÊN DI ĐỘNG */
        .sidebar-backdrop {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(8, 4, 2, 0.76);
            backdrop-filter: blur(4px);
            z-index: 1040;
        }
        .sidebar-backdrop.active { display: block; }

        /* THANH CÔNG CỤ & BỘ LỌC (SIDEBAR COLLAPSIBLE) */
        .sidebar {
            width: 310px;
            min-width: 310px;
            background: var(--sidebar-bg);
            border-right: 1px solid rgba(180, 83, 9, 0.32);
            box-shadow: 8px 0 32px rgba(0, 0, 0, 0.65);
            padding: 20px 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            overflow-y: auto;
            max-height: 100vh;
            position: sticky;
            top: 0;
            z-index: 1050;
            transition: margin-left 0.28s cubic-bezier(0.4, 0, 0.2, 1), transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.22s ease;
        }
        .sidebar.collapsed {
            margin-left: -310px;
            opacity: 0;
            pointer-events: none;
        }
        .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(180, 83, 9, 0.28);
        }
        .sidebar h2 {
            margin: 0;
            font-size: 16.5px;
            font-family: var(--font-display);
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.2px;
        }
        .sidebar h3 {
            margin: 2px 0 0 0;
            font-size: 13px;
            font-family: var(--font-display);
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }
        .btn-collapse-double {
            background: rgba(180, 83, 9, 0.14);
            border: 1px solid rgba(180, 83, 9, 0.38);
            color: var(--amber-light);
            border-radius: 7px;
            padding: 4px 9px;
            font-family: var(--font-mono);
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.18s ease;
        }
        .btn-collapse-double:hover {
            background: rgba(245, 158, 11, 0.25);
            border-color: var(--amber-cyber);
            color: #fff;
        }

        /* FILTER PILLS TRONG SIDEBAR (GIỐNG MẪU) */
        .quick-pills-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .filter-pill {
            background: rgba(26, 16, 9, 0.9);
            border: 1px solid rgba(180, 83, 9, 0.35);
            color: var(--text-secondary);
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.18s ease;
        }
        .filter-pill:hover, .filter-pill.active {
            background: linear-gradient(135deg, rgba(180, 83, 9, 0.45), rgba(245, 158, 11, 0.25));
            border-color: var(--amber-cyber);
            color: var(--amber-pale);
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.22);
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, rgba(180, 83, 9, 0.1), rgba(180, 83, 9, 0.38), rgba(180, 83, 9, 0.1));
            margin: 4px 0;
        }

        /* VÙNG NỘI DUNG CHÍNH (MAIN CONTENT) - CĂN RỘNG HỢP LÝ */
        .main-area {
            flex: 1;
            min-width: 0;
            padding: 22px 34px 44px 34px;
            max-width: 1640px;
            margin: 0 auto;
            overflow-y: auto;
            transition: all 0.28s ease;
        }

        /* THANH HEADER ĐẦU TRANG (TOP NAVBAR GIỐNG MẪU) */
        .top-utility-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding-bottom: 16px;
            margin-bottom: 22px;
            border-bottom: 1px solid rgba(180, 83, 9, 0.26);
            flex-wrap: wrap;
        }
        .top-bar-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .top-bar-title {
            font-family: var(--font-display);
            font-size: 19px;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.3px;
            margin: 0;
        }
        .btn-toggle-taskbar {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(34, 20, 11, 0.92);
            border: 1px solid var(--copper-border);
            color: var(--amber-light);
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .btn-toggle-taskbar:hover {
            border-color: var(--amber-cyber);
            background: rgba(180, 83, 9, 0.25);
            color: #ffffff;
            box-shadow: 0 0 14px rgba(245, 158, 11, 0.22);
        }
        .top-bar-actions {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .top-badge-btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(26, 16, 9, 0.92);
            border: 1px solid rgba(180, 83, 9, 0.36);
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.18s ease;
        }
        .top-badge-btn:hover {
            border-color: var(--amber-cyber);
            color: var(--amber-pale);
            background: rgba(180, 83, 9, 0.18);
        }

        /* BANNER TRUNG TÂM CYBER AMBER & BLUEPRINT (ĐÃ LƯỢC BỎ DÒNG CHỮ PHỤ ĐỀ) */
        .tech-hero-banner {
            position: relative;
            background:
                radial-gradient(circle at 50% 42%, rgba(245, 158, 11, 0.18) 0%, rgba(180, 83, 9, 0.08) 42%, transparent 72%),
                linear-gradient(135deg, #170e07 0%, #211309 48%, #120b06 100%);
            border: 1px solid rgba(217, 119, 6, 0.48);
            outline: 1px solid rgba(245, 158, 11, 0.16);
            outline-offset: -6px;
            border-radius: 16px;
            padding: 34px 32px 26px 32px;
            margin-bottom: 28px;
            text-align: center;
            overflow: hidden;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.65), inset 0 0 36px rgba(180, 83, 9, 0.12);
        }
        /* Thanh notch kim loại đồng phía trên banner */
        .tech-hero-banner::before {
            content: "";
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 240px;
            height: 7px;
            background: linear-gradient(90deg, rgba(180, 83, 9, 0.3), rgba(245, 158, 11, 0.75), rgba(180, 83, 9, 0.3));
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            box-shadow: 0 2px 12px rgba(245, 158, 11, 0.45);
        }
        .hero-decor-left {
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 230px;
            pointer-events: none;
            opacity: 0.75;
        }
        .hero-decor-right {
            position: absolute;
            right: 0;
            top: 0;
            bottom: 0;
            width: 250px;
            pointer-events: none;
            opacity: 0.55;
        }
        .hero-title-glow {
            position: relative;
            z-index: 2;
            margin: 0 0 14px 0;
            font-family: var(--font-display);
            font-size: 33px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(180deg, #fff7ed 0%, #fbbf24 52%, #d97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 4px 18px rgba(245, 158, 11, 0.32));
        }
        .hero-indicators {
            position: relative;
            z-index: 2;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .hero-indicator-bar {
            width: 32px;
            height: 4px;
            border-radius: 999px;
            background: var(--amber-cyber);
            box-shadow: 0 0 10px var(--amber-cyber);
        }
        .hero-indicator-bar.muted {
            width: 24px;
            background: rgba(180, 83, 9, 0.45);
            box-shadow: none;
        }
        .tech-badge {
            display: inline-block;
            background: rgba(180, 83, 9, 0.25);
            border: 1px solid rgba(245, 158, 11, 0.5);
            color: var(--amber-light);
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 999px;
            letter-spacing: 0.5px;
        }

        /* TÁCH KHỐI RÕ NÉT (.glass-card) VỚI VIỀN BO GÓC KÉP & HIGHLIGHT ĐỒNG */
        .glass-card {
            position: relative;
            background: var(--card-bg);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(180, 83, 9, 0.38);
            box-shadow:
                0 14px 34px rgba(0, 0, 0, 0.58),
                inset 0 0 0 1px rgba(245, 158, 11, 0.08),
                inset 0 1px 0 rgba(251, 191, 36, 0.16);
            border-radius: 14px;
            padding: 22px;
            transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease, background 0.22s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .glass-card:hover {
            background: var(--card-bg-hover);
            border-color: var(--amber-cyber);
            box-shadow:
                0 18px 42px rgba(0, 0, 0, 0.72),
                0 0 22px rgba(180, 83, 9, 0.28),
                inset 0 0 0 1px rgba(245, 158, 11, 0.25);
            transform: translateY(-2px);
        }
        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(min(100%, 440px), 1fr));
            gap: 24px;
        }

        /* HEADER CỦA THẺ MÔ HÌNH (ICON ĐỒNG + STATUS PILL COMPLETED) */
        .card-top-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 14px;
        }
        .card-copper-icon {
            width: 36px;
            height: 36px;
            border-radius: 9px;
            background: rgba(180, 83, 9, 0.2);
            border: 1px solid rgba(217, 119, 6, 0.45);
            color: var(--amber-light);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            box-shadow: inset 0 0 10px rgba(245, 158, 11, 0.12);
        }
        .status-pill-completed {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--emerald-bg);
            border: 1px solid var(--emerald-border);
            color: var(--emerald-text);
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 999px;
            letter-spacing: 0.2px;
        }
        .status-pill-pending {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(180, 83, 9, 0.26);
            border: 1px solid rgba(245, 158, 11, 0.5);
            color: var(--amber-light);
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 999px;
        }
        .card-model-title {
            margin: 0 0 12px 0;
            font-family: var(--font-display);
            font-size: 19px;
            font-weight: 700;
            color: var(--amber-light);
            letter-spacing: -0.2px;
            cursor: pointer;
            transition: color 0.18s ease;
        }
        .card-model-title:hover {
            color: var(--amber-pale);
            text-decoration: underline;
        }

        /* KHUNG PREVIEW SƠ ĐỒ MINI TRÊN THẺ (GIỐNG MẪU HÌNH 1.1) */
        .card-schematic-preview {
            background: rgba(42, 24, 12, 0.68);
            border: 1px solid rgba(180, 83, 9, 0.35);
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .card-schematic-preview:hover {
            border-color: var(--amber-cyber);
            background: rgba(56, 32, 15, 0.78);
        }
        .card-meta-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 14px;
            font-size: 13.5px;
            color: var(--text-secondary);
        }
        .card-meta-row {
            display: flex;
            align-items: flex-start;
            gap: 9px;
            line-height: 1.5;
        }
        .card-meta-icon {
            color: var(--amber-cyber);
            font-size: 14px;
            margin-top: 1px;
            flex-shrink: 0;
        }

        /* HIGHLIGHT Ý CHÍNH & BADGE KÝ HIỆU ĐỒNG NÓNG (DEVICES BADGES) */
        .devices-section-label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: lowercase;
            letter-spacing: 0.4px;
            margin-bottom: 8px;
        }
        .device-badges-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin-bottom: 16px;
        }
        .copper-device-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: linear-gradient(180deg, rgba(180, 83, 9, 0.28) 0%, rgba(120, 53, 15, 0.38) 100%);
            border: 1px solid rgba(217, 119, 6, 0.55);
            color: var(--amber-pale);
            font-family: var(--font-mono);
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.18s ease;
            box-shadow: inset 0 1px 0 rgba(251, 191, 36, 0.2);
        }
        .copper-device-badge:hover {
            background: linear-gradient(180deg, rgba(217, 119, 6, 0.48) 0%, rgba(180, 83, 9, 0.58) 100%);
            border-color: var(--amber-light);
            color: #ffffff;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }

        /* KHỐI NHẬP THIẾT BỊ / KHÁI NIỆM NHIỀU DÒNG TRONG MODAL CRUD */
        .crud-device-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 12px;
        }
        .crud-device-item {
            background: rgba(20, 12, 6, 0.85);
            border: 1px solid rgba(217, 119, 6, 0.42);
            border-radius: 10px;
            padding: 14px;
            box-shadow: inset 0 0 14px rgba(180, 83, 9, 0.08);
        }
        .crud-device-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 6px;
            border-bottom: 1px dashed rgba(180, 83, 9, 0.35);
        }
        .crud-device-grid-top {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 12px;
            margin-bottom: 10px;
        }
        .crud-device-grid-bottom {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        /* LƯỚI NÚT & BỐ CỤC CO GIÃN */
        .card-actions-grid {
            display: grid;
            grid-template-columns: 1.5fr 1.2fr 0.8fr 0.8fr;
            gap: 8px;
            margin-top: 12px;
        }
        .form-grid-2 {
            display: grid;
            grid-template-columns: 1.6fr 1fr;
            gap: 14px;
            margin-bottom: 14px;
        }
        .detail-top-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 22px;
            margin-bottom: 24px;
        }
        .detail-gallery-grid {
            display: grid;
            grid-template-columns: 1.6fr 1fr;
            gap: 22px;
        }
        .real-images-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(min(100%, 240px), 1fr));
            gap: 16px;
        }
        .quiz-answer-grid {
            display: grid;
            grid-template-columns: 1.5fr 0.9fr 1.1fr auto;
            gap: 10px;
            align-items: end;
        }

        /* INPUTS & BUTTONS THEO TÔNG TECH-BROWN / COPPER */
        label {
            display: block;
            font-size: 12.5px;
            color: var(--text-secondary);
            margin-bottom: 6px;
            font-weight: 500;
        }
        input[type="text"], input[type="number"], input[type="password"], select, textarea {
            width: 100%;
            background: rgba(12, 7, 4, 0.92);
            border: 1px solid rgba(180, 83, 9, 0.42);
            color: var(--text-main);
            border-radius: 8px;
            padding: 9px 12px;
            font-family: var(--font-sans);
            font-size: 13.5px;
            outline: none;
            transition: border-color 0.18s ease, box-shadow 0.18s ease;
        }
        textarea {
            line-height: 1.5;
            resize: vertical;
        }
        input:focus, select:focus, textarea:focus {
            border-color: var(--amber-cyber);
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.22);
        }
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 9px 13px;
            border-radius: 8px;
            font-family: var(--font-sans);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.18s ease;
            border: 1px solid transparent;
            text-decoration: none;
            text-align: center;
            line-height: 1.3;
        }
        .btn-primary {
            background: linear-gradient(135deg, #b45309 0%, #d97706 100%);
            color: #fffbeb;
            border-color: rgba(251, 191, 36, 0.55);
            box-shadow: 0 4px 14px rgba(180, 83, 9, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
            border-color: #fde68a;
            color: #ffffff;
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5);
            transform: translateY(-1px);
        }
        .btn-secondary {
            background: rgba(36, 22, 12, 0.9);
            color: var(--text-secondary);
            border-color: rgba(180, 83, 9, 0.38);
        }
        .btn-secondary:hover {
            border-color: var(--amber-cyber);
            color: var(--amber-light);
            background: rgba(52, 30, 15, 0.95);
        }
        .btn-secondary.active-band {
            border-color: var(--amber-cyber);
            background: rgba(180, 83, 9, 0.38);
            color: var(--amber-pale);
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.25);
        }
        .btn-full { width: 100%; }
        code {
            font-family: var(--font-mono);
            background: rgba(180, 83, 9, 0.2);
            color: var(--amber-light);
            border: 1px solid rgba(217, 119, 6, 0.4);
            padding: 2px 7px;
            border-radius: 5px;
            font-size: 12.5px;
        }

        /* MODALS */
        .modal-backdrop {
            position: fixed;
            inset: 0;
            background: rgba(8, 4, 2, 0.84);
            backdrop-filter: blur(6px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1100;
            padding: 18px;
        }
        .modal-backdrop.active { display: flex; }
        .modal-dialog {
            background: #160d07;
            border: 1px solid var(--amber-cyber);
            box-shadow: 0 24px 64px rgba(0, 0, 0, 0.9), 0 0 32px rgba(180, 83, 9, 0.26);
            border-radius: 16px;
            width: 100%;
            max-width: 940px;
            max-height: 92vh;
            overflow-y: auto;
            padding: 26px 28px;
            position: relative;
        }
        .modal-close {
            position: sticky;
            top: 0;
            float: right;
            background: rgba(26, 16, 9, 0.95);
            border: 1px solid rgba(217, 119, 6, 0.5);
            color: var(--amber-light);
            border-radius: 7px;
            padding: 5px 11px;
            cursor: pointer;
            font-size: 15px;
            z-index: 30;
        }
        .modal-close:hover {
            border-color: #f87171;
            color: #f87171;
        }

        /* DIAGRAM BOX CREAM-SAND & SVG HOTSPOTS */
        .diagram-box {
            position: relative;
            width: 100%;
            max-width: 700px;
            margin: 14px auto;
            border: 2px solid var(--copper-bright);
            outline: 1px solid rgba(245, 158, 11, 0.35);
            outline-offset: 3px;
            border-radius: 12px;
            background-color: var(--cream-sand);
            background-image:
                linear-gradient(rgba(180, 83, 9, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(180, 83, 9, 0.08) 1px, transparent 1px);
            background-size: 20px 20px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55), 0 0 20px rgba(180, 83, 9, 0.2);
            padding: 12px;
            user-select: none;
        }
        .diagram-box svg {
            display: block;
            width: 100%;
            height: auto;
        }
        .svg-hotspot {
            cursor: pointer;
            transition: all 0.18s ease;
        }
        .svg-hotspot:hover .shape-elem {
            stroke: #b45309 !important;
            fill: #fef3c7 !important;
            filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.75));
        }
        .svg-hotspot:hover .wire-path {
            stroke: #d97706 !important;
            stroke-width: 4px !important;
            filter: drop-shadow(0 0 6px rgba(245, 158, 11, 0.7));
        }
        .svg-hotspot:hover .node-elem {
            fill: #d97706 !important;
            r: 8.5px;
            filter: drop-shadow(0 0 9px rgba(245, 158, 11, 0.9));
        }
        .svg-hotspot:hover text {
            fill: #92400e !important;
            font-weight: bold;
        }

        /* BẢNG MÀU & BẢNG KÝ HIỆU DUNG SAI (TECH TABLE) */
        .tech-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 13.5px;
            border: 1px solid rgba(217, 119, 6, 0.42);
            border-radius: 8px;
            overflow: hidden;
        }
        .tech-table th {
            background: rgba(180, 83, 9, 0.28);
            color: var(--amber-pale);
            padding: 9px 10px;
            text-align: center;
            border: 1px solid rgba(217, 119, 6, 0.35);
            font-weight: 700;
        }
        .tech-table td {
            padding: 7px 10px;
            text-align: center;
            border: 1px solid rgba(217, 119, 6, 0.24);
            font-weight: 600;
        }

        /* CUSTOM IMAGE HOTSPOTS */
        .custom-diagram-wrapper {
            position: relative;
            display: block;
            max-width: 700px;
            width: 100%;
            margin: 14px auto;
            border: 2px solid var(--copper-bright);
            border-radius: 12px;
            background: var(--cream-sand);
            box-shadow: 0 0 24px rgba(180, 83, 9, 0.25);
            overflow: hidden;
        }
        .custom-diagram-wrapper img {
            display: block;
            width: 100%;
            height: auto;
            max-height: 420px;
            object-fit: contain;
        }
        .custom-hs-box {
            position: absolute;
            border: 2px dashed rgba(180, 83, 9, 0.9);
            background: rgba(245, 158, 11, 0.18);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.18s ease;
        }
        .custom-hs-box:hover {
            border: 2.5px solid #d97706;
            background: rgba(245, 158, 11, 0.34);
            box-shadow: 0 0 16px rgba(245, 158, 11, 0.8);
            z-index: 20;
        }
        .hs-tag {
            position: absolute;
            top: -21px;
            left: 0;
            background: #160d07;
            color: var(--amber-light);
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 600;
            padding: 1px 6px;
            border-radius: 4px;
            border: 1px solid var(--amber-cyber);
            white-space: nowrap;
            pointer-events: none;
        }

        /* FLOATING TOOLTIP */
        #floating-tooltip {
            position: fixed;
            display: none;
            background: rgba(20, 12, 6, 0.96);
            color: var(--amber-pale);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            pointer-events: none;
            z-index: 9999;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.7);
            border: 1px solid var(--amber-cyber);
            white-space: nowrap;
        }

        /* HOTSPOT EDITOR STAGE */
        .canvas-stage-wrap {
            display: flex;
            justify-content: center;
            background: #0c0704;
            padding: 12px;
            border-radius: 10px;
            border: 1px dashed rgba(217, 119, 6, 0.5);
            user-select: none;
            overflow: hidden;
        }
        #editor-stage {
            position: relative;
            display: inline-block;
            max-width: 100%;
            cursor: crosshair;
            line-height: 0;
            touch-action: none;
        }
        #editor-stage img {
            display: block;
            max-width: 100%;
            max-height: 380px;
            width: auto;
            height: auto;
            background: var(--cream-sand);
            border-radius: 6px;
            pointer-events: none;
        }
        .drawn-box {
            position: absolute;
            border: 2px solid #d97706;
            background: rgba(245, 158, 11, 0.25);
            border-radius: 4px;
        }
        .drawn-box-label {
            position: absolute;
            top: -20px;
            left: 0;
            background: #140c06;
            color: var(--amber-light);
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid var(--amber-cyber);
            white-space: nowrap;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .del-hs-btn {
            color: #f87171;
            cursor: pointer;
            font-weight: bold;
            margin-left: 4px;
            padding: 0 3px;
        }
        #rubber-band {
            position: absolute;
            display: none;
            border: 2px dashed var(--amber-light);
            background: rgba(245, 158, 11, 0.28);
            pointer-events: none;
        }

        /* TOAST, ALERTS & QUIZ FEEDBACK */
        #toast-box {
            position: fixed;
            bottom: 22px;
            right: 22px;
            max-width: calc(100vw - 44px);
            background: #180f08;
            border: 1px solid var(--amber-cyber);
            color: var(--amber-pale);
            padding: 12px 18px;
            border-radius: 10px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.75);
            z-index: 9999;
            display: none;
            font-weight: 600;
        }
        .error-alert {
            background: rgba(239, 68, 68, 0.16);
            border: 1px solid #ef4444;
            color: #fca5a5;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 13.5px;
            display: none;
        }
        .info-alert {
            background: rgba(180, 83, 9, 0.16);
            border: 1px solid rgba(245, 158, 11, 0.42);
            color: var(--amber-pale);
            padding: 14px 18px;
            border-radius: 10px;
            font-size: 14px;
        }
        .quiz-feedback-ok {
            background: rgba(16, 185, 129, 0.18);
            border: 1px solid #10b981;
            color: #a7f3d0;
            padding: 14px 16px;
            border-radius: 10px;
            margin-top: 12px;
            font-size: 14px;
            line-height: 1.6;
        }
        .quiz-feedback-err {
            background: rgba(239, 68, 68, 0.18);
            border: 1px solid #ef4444;
            color: #fecaca;
            padding: 14px 16px;
            border-radius: 10px;
            margin-top: 12px;
            font-size: 14px;
            line-height: 1.6;
        }

        /* ==========================================
           TỐI ƯU HÓA GIAO DIỆN DI ĐỘNG (MOBILE RESPONSIVE)
           ========================================== */
        @media (max-width: 900px) {
            .icon-rail { display: none; }
            .sidebar {
                position: fixed;
                left: 0;
                top: 0;
                bottom: 0;
                width: 86vw;
                max-width: 320px;
                min-width: unset;
                height: 100vh;
                max-height: 100vh;
                margin-left: 0 !important;
                transform: translateX(0);
                opacity: 1 !important;
                pointer-events: auto !important;
            }
            .sidebar.collapsed {
                transform: translateX(-105%);
                pointer-events: none !important;
            }
            .main-area {
                padding: 14px 14px 34px 14px;
                width: 100%;
            }
            .tech-hero-banner {
                padding: 24px 16px 20px 16px;
                margin-bottom: 20px;
            }
            .hero-decor-left, .hero-decor-right {
                opacity: 0.25;
            }
            .hero-title-glow {
                font-size: 23px !important;
                line-height: 1.3;
            }
            .models-grid {
                grid-template-columns: 1fr;
                gap: 16px;
            }
            .card-actions-grid {
                grid-template-columns: 1fr 1fr;
            }
            .form-grid-2,
            .detail-top-grid,
            .detail-gallery-grid,
            .quiz-answer-grid,
            .crud-device-grid-top,
            .crud-device-grid-bottom {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            .modal-backdrop { padding: 8px; }
            .modal-dialog {
                padding: 16px 14px;
                max-height: 94vh;
                border-radius: 12px;
            }
            .glass-card { padding: 16px; }
            #floating-tooltip { display: none !important; }
        }

        @media (max-width: 480px) {
            .top-utility-bar {
                flex-direction: column;
                align-items: stretch;
            }
            .top-bar-left {
                justify-content: space-between;
            }
            .top-bar-actions {
                justify-content: space-between;
            }
            .btn {
                padding: 9px 10px;
                font-size: 12.5px;
            }
        }
    </style>
</head>
<body>
    <!-- THANH ICON RAIL DỌC BÊN TRÁI (GIỐNG MẪU DASHBOARD) -->
    <nav class="icon-rail" aria-label="Quick Navigation">
        <div class="rail-logo" onclick="backToMainView()" title="Trang chủ Model ĐĐT">⚡</div>
        <button class="rail-btn active" onclick="toggleSidebar()" title="Đóng / Mở Thanh Công cụ & Bộ lọc">⊞</button>
        <button class="rail-btn" onclick="openCrudModal(null)" title="Tạo Mô hình mới">➕</button>
        <button class="rail-btn" onclick="setQuickFilter('')" title="Hiển thị toàn bộ mô hình">〰</button>
        <a href="/api/export" download="data.json" class="rail-btn" title="Xuất (Export) data.json" style="text-decoration:none;">📤</a>
        <div class="rail-spacer"></div>
        <button class="rail-btn" onclick="toggleSidebar(true)" title="Cấu hình & Đồng bộ GitHub">⚙️</button>
    </nav>

    <!-- LỚP NỀN MỜ KHI MỞ SIDEBAR TRÊN MOBILE -->
    <div id="sidebar-backdrop" class="sidebar-backdrop" onclick="toggleSidebar(false)"></div>

    <!-- SIDEBAR: THANH CÔNG CỤ & BỘ LỌC -->
    <aside id="app-sidebar" class="sidebar">
        <div class="sidebar-header">
            <h2>Thanh Công cụ & Bộ lọc</h2>
            <button class="btn-collapse-double" onclick="toggleSidebar(false)" title="Thu gọn thanh công cụ">
                &lt;&lt;
            </button>
        </div>

        <button class="btn btn-primary btn-full" onclick="openCrudModal(null)">➕ Tạo Mô hình mới</button>

        <div>
            <label>Tìm theo Tên (Mô hình / Thiết bị)</label>
            <input type="text" id="filter-name" placeholder="VD: Nguồn, Điện trở, Cuộn dây, Dòng điện..." oninput="renderMainWorkspace()" />
        </div>

        <!-- BỘ LỌC NHANH BẰNG PILL TAGS (THEO MẪU) -->
        <div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <label style="margin:0;">Filters (Chủ đề nhanh)</label>
                <span style="font-size:11.5px; color:var(--amber-light); cursor:pointer;" onclick="resetAllFilters()">Xóa lọc</span>
            </div>
            <div class="quick-pills-wrap">
                <span class="filter-pill active" id="pill-all" onclick="setQuickFilter('')">Tất cả</span>
                <span class="filter-pill" onclick="setQuickFilter('Nguồn')">Nguồn điện</span>
                <span class="filter-pill" onclick="setQuickFilter('Tải')">Phụ tải</span>
                <span class="filter-pill" onclick="setQuickFilter('Nhánh')">Nhánh</span>
                <span class="filter-pill" onclick="setQuickFilter('Nút')">Nút</span>
                <span class="filter-pill" onclick="setQuickFilter('Vòng')">Mạch vòng</span>
                <span class="filter-pill" onclick="setQuickFilter('Dòng điện')">Dòng điện</span>
                <span class="filter-pill" onclick="setQuickFilter('Điện trở')">Điện trở</span>
                <span class="filter-pill" onclick="setQuickFilter('Cuộn dây')">Cuộn dây</span>
            </div>
        </div>

        <div class="divider"></div>
        <h3>🔎 Bộ lọc chuyên sâu</h3>
        <div>
            <label>Tìm theo Khái niệm</label>
            <input type="text" id="filter-concept" placeholder="VD: mạch kín, từ trường, nhiệt năng..." oninput="renderMainWorkspace()" />
        </div>
        <div>
            <label>Tìm theo Ký hiệu kỹ thuật</label>
            <input type="text" id="filter-symbol" placeholder="VD: R, L, i, u_ab, E1, Nút A..." oninput="renderMainWorkspace()" />
        </div>
        <div>
            <label>Lọc theo Trạng thái</label>
            <select id="filter-status" onchange="renderMainWorkspace()">
                <option value="Tất cả">Tất cả trạng thái</option>
                <option value="completed">completed</option>
                <option value="pending">pending</option>
            </select>
        </div>

        <div class="divider"></div>
        <h3>📦 Sao lưu & Chia sẻ (JSON)</h3>
        <a href="/api/export" class="btn btn-secondary btn-full" download="data.json">📤 Xuất (Export) data.json</a>
        <div style="margin-top: 4px;">
            <label>📥 Nhập (Import) file data.json</label>
            <input type="file" id="import-json-input" accept=".json" onchange="handleImportJson(event)" style="font-size:12px;" />
        </div>

        <div class="divider"></div>
        <h3>☁️ Đồng bộ Đám mây</h3>
        <div id="github-status-text" style="font-size:12.5px; color:var(--text-muted);">
            🟢 Lưu trực tiếp trên ổ cứng Server (<code>data.json</code>)
        </div>
        <details style="font-size:12.5px; color:var(--text-secondary);">
            <summary style="cursor:pointer; color:var(--amber-light); font-weight:600;">⚙️ Cấu hình GitHub Auto-Sync</summary>
            <div style="margin-top:8px; display:flex; flex-direction:column; gap:6px;">
                <input type="text" id="gh-repo" placeholder="ten-ban/model-ddt" />
                <input type="password" id="gh-token" placeholder="GitHub Token (ghp_...)" />
                <input type="text" id="gh-branch" value="main" placeholder="Branch (main)" />
                <button class="btn btn-primary btn-full" onclick="saveGithubConfig()">🔗 Kết nối GitHub</button>
            </div>
        </details>

        <div class="divider"></div>
        <div style="font-size:12.5px; color:var(--text-muted); display:flex; justify-content:space-between;">
            <span>Tổng số mô hình:</span>
            <b id="total-models-count" style="color:var(--amber-light); font-family:var(--font-mono);">0</b>
        </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main-area">
        <!-- THANH HEADER ĐẦU TRANG (GIỐNG MẪU) -->
        <header class="top-utility-bar">
            <div class="top-bar-left">
                <button id="btn-open-taskbar" class="btn-toggle-taskbar" onclick="toggleSidebar()">
                    <span id="toggle-taskbar-icon">☰</span>
                    <span id="toggle-taskbar-text">Thanh Công cụ</span>
                </button>
                <h2 class="top-bar-title">Model ĐĐT — Kỹ thuật Điện - Điện tử</h2>
            </div>
            <div class="top-bar-actions">
                <button class="top-badge-btn" onclick="openCrudModal(null)" title="Thêm mô hình mới">
                    ➕ Thêm Mô hình
                </button>
                <a href="/api/export" download="data.json" class="top-badge-btn" title="Tải file data.json">
                    💾 Backup JSON
                </a>
                <button class="top-badge-btn" onclick="toggleSidebar(true)" title="Mở bộ lọc và cấu hình">
                    ⚙️ Bộ lọc & Sync
                </button>
            </div>
        </header>

        <!-- VIEW 1: MAIN WORKSPACE -->
        <div id="view-main">
            <!-- BANNER TRUNG TÂM CYBER AMBER & BLUEPRINT (ĐÃ XÓA DÒNG CHỮ PHỤ ĐỀ THEO YÊU CẦU) -->
            <div class="tech-hero-banner">
                <!-- Họa tiết mạch đồng phát sáng bên trái -->
                <svg class="hero-decor-left" viewBox="0 0 240 180" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M-10 35 L75 35 L125 85 L75 135 L-10 135" stroke="url(#copperGrad)" stroke-width="3.5" opacity="0.85"/>
                    <path d="M-10 55 L65 55 L95 85 L65 115 L-10 115" stroke="#f59e0b" stroke-width="1.5" opacity="0.55"/>
                    <circle cx="125" cy="85" r="5" fill="#fbbf24" />
                    <defs>
                        <linearGradient id="copperGrad" x1="0" y1="0" x2="200" y2="180" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#b45309"/>
                            <stop offset="50%" stop-color="#fbbf24"/>
                            <stop offset="100%" stop-color="#78350f"/>
                        </linearGradient>
                    </defs>
                </svg>
                <!-- Họa tiết bản vẽ tọa độ kỹ thuật bên phải -->
                <svg class="hero-decor-right" viewBox="0 0 260 180" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="190" cy="125" r="78" stroke="#d97706" stroke-width="1" stroke-dasharray="4 4" opacity="0.6"/>
                    <circle cx="190" cy="125" r="48" stroke="#f59e0b" stroke-width="1.2" opacity="0.5"/>
                    <line x1="80" y1="125" x2="260" y2="125" stroke="#b45309" stroke-width="1" opacity="0.6"/>
                    <line x1="190" y1="15" x2="190" y2="180" stroke="#b45309" stroke-width="1" opacity="0.6"/>
                    <line x1="120" y1="55" x2="245" y2="175" stroke="#f59e0b" stroke-width="1.2" opacity="0.45"/>
                    <circle cx="156" cy="91" r="3.5" fill="#fbbf24"/>
                    <circle cx="190" cy="77" r="3.5" fill="#fbbf24"/>
                </svg>

                <h1 class="hero-title-glow">Model ĐĐT - Kỹ thuật Điện - Điện tử</h1>
                <div class="hero-indicators">
                    <span class="hero-indicator-bar"></span>
                    <span class="hero-indicator-bar muted"></span>
                </div>
            </div>

            <div id="workspace-container"></div>
        </div>

        <!-- VIEW 2: DEVICE DETAIL PAGE -->
        <div id="view-device-detail" style="display:none;">
            <button class="btn btn-secondary" onclick="backToMainView()" style="margin-bottom:18px;">⬅️ Quay lại Bảng điều khiển chính</button>
            <div id="device-detail-content"></div>
        </div>
    </main>

    <!-- MODAL 1: SƠ ĐỒ MÔ HÌNH & KÝ HIỆU THIẾT BỊ -->
    <div class="modal-backdrop" id="modal-model">
        <div class="modal-dialog">
            <button class="modal-close" onclick="closeModal('modal-model')">✕</button>
            <div id="modal-model-body"></div>
        </div>
    </div>

    <!-- MODAL 2: VISUAL HOTSPOT EDITOR -->
    <div class="modal-backdrop" id="modal-hotspot">
        <div class="modal-dialog">
            <button class="modal-close" onclick="closeModal('modal-hotspot')">✕</button>
            <div id="modal-hotspot-body"></div>
        </div>
    </div>

    <!-- MODAL 3: THÊM / SỬA MÔ HÌNH (CRUD - HỖ TRỢ KHÁI NIỆM & CHI TIẾT NHIỀU DÒNG) -->
    <div class="modal-backdrop" id="modal-crud">
        <div class="modal-dialog">
            <button class="modal-close" onclick="closeModal('modal-crud')">✕</button>
            <h2 id="crud-modal-title" style="margin-top:0; font-family:var(--font-display); color:var(--amber-light);">📝 Thêm / Chỉnh sửa Mô hình ĐĐT</h2>
            <div id="crud-error-box" class="error-alert"></div>
            <input type="hidden" id="crud-id" />
            <div class="form-grid-2">
                <div>
                    <label>Tên mô hình (*)</label>
                    <input type="text" id="crud-title" placeholder="VD: Hình 1.1: Mô hình mạch điện" />
                </div>
                <div>
                    <label>Ký hiệu mô hình (*)</label>
                    <input type="text" id="crud-symbol" placeholder="VD: H1.1" />
                </div>
            </div>
            <div class="form-grid-2">
                <div>
                    <label>Danh mục / Học phần (*)</label>
                    <input type="text" id="crud-category" />
                </div>
                <div>
                    <label>Trạng thái (*)</label>
                    <select id="crud-status">
                        <option value="completed">completed</option>
                        <option value="pending">pending</option>
                    </select>
                </div>
            </div>
            <div style="margin-bottom:14px;">
                <label>Khái niệm & Nguyên lý mô hình (*) — Có thể nhấn Enter xuống dòng</label>
                <textarea id="crud-concept" rows="3" placeholder="Mô tả khái niệm và nguyên lý hoạt động tổng quát của mô hình (hỗ trợ nhiều dòng)..."></textarea>
            </div>
            <div class="form-grid-2">
                <div>
                    <label>Tải ảnh sơ đồ tùy chỉnh (.png, .jpg, .webp)</label>
                    <input type="file" id="crud-diagram-file" accept="image/*" />
                </div>
                <div>
                    <label>Hoặc nhập URL ảnh sơ đồ</label>
                    <input type="text" id="crud-diagram-url" placeholder="https://example.com/diagram.png" />
                </div>
            </div>
            <div style="margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
                    <label style="margin:0; font-size:13.5px; color:var(--amber-light); font-weight:700;">
                        ⚡ Danh sách Thiết bị / Khái niệm trên mô hình (*)
                    </label>
                    <button type="button" class="btn btn-secondary" onclick="addCrudDeviceRow()">
                        ➕ Thêm Thiết bị / Khái niệm mới
                    </button>
                </div>
                <div style="font-size:12px; color:var(--text-muted); margin-bottom:10px; line-height:1.5;">
                    💡 Mỗi mục tương ứng với 1 phần tử hoặc khái niệm. Bạn có thể <b>nhấn Enter xuống dòng thoải mái</b> trong ô <b>Khái niệm</b> và ô <b>Nội dung chi tiết / Công thức / Ví dụ</b> (Để trống hoặc nhập <code>-</code> ở ô Ký hiệu nếu khái niệm không có ký hiệu riêng trên hình).
                </div>
                <div id="crud-devices-list" class="crud-device-list"></div>
                <button type="button" class="btn btn-secondary btn-full" onclick="addCrudDeviceRow()" style="border-style:dashed;">
                    ➕ Thêm dòng Thiết bị / Khái niệm tiếp theo
                </button>
            </div>
            <button class="btn btn-primary btn-full" onclick="submitCrudForm()">💾 Lưu dữ liệu</button>
        </div>
    </div>

    <div id="floating-tooltip"></div>
    <div id="toast-box"></div>

    <script>
        let modelsData = [];
        let selectedModelId = null;
        let selectedDeviceId = null;
        let editorHotspots = [];
        let editorModelId = null;
        let crudDevicesDraft = [];

        // Trạng thái Mô hình hỏi đáp (Quiz) Điện trở
        let quizState = {
            bandCount: 4,
            bands: [],
            ohmValue: 0,
            toleranceValue: 5
        };

        const RESISTOR_COLORS = [
            { key: 'den', name: 'Đen', hex: '#111827', textHex: '#ffffff', digit: 0, multExp: 0, tol: null },
            { key: 'nau', name: 'Nâu', hex: '#78350f', textHex: '#ffffff', digit: 1, multExp: 1, tol: 1 },
            { key: 'do', name: 'Đỏ', hex: '#dc2626', textHex: '#ffffff', digit: 2, multExp: 2, tol: 2 },
            { key: 'cam', name: 'Cam', hex: '#ea580c', textHex: '#ffffff', digit: 3, multExp: 3, tol: null },
            { key: 'vang', name: 'Vàng', hex: '#facc15', textHex: '#0f172a', digit: 4, multExp: 4, tol: null },
            { key: 'xanhluc', name: 'Xanh lục', hex: '#16a34a', textHex: '#ffffff', digit: 5, multExp: 5, tol: 0.5 },
            { key: 'xanhlam', name: 'Xanh lam', hex: '#0284c7', textHex: '#ffffff', digit: 6, multExp: 6, tol: null },
            { key: 'tim', name: 'Tím', hex: '#7e22ce', textHex: '#ffffff', digit: 7, multExp: 7, tol: null },
            { key: 'xam', name: 'Xám', hex: '#6b7280', textHex: '#ffffff', digit: 8, multExp: 8, tol: null },
            { key: 'trang', name: 'Trắng', hex: '#f8fafc', textHex: '#0f172a', digit: 9, multExp: 9, tol: null },
            { key: 'kimnhu', name: 'Kim nhũ (Nhũ vàng)', hex: '#eab308', textHex: '#0f172a', digit: null, multExp: -1, tol: 5 },
            { key: 'ngannhu', name: 'Ngân nhũ (Nhũ bạc)', hex: '#cbd5e1', textHex: '#0f172a', digit: null, multExp: -2, tol: 10 }
        ];

        const tooltipEl = document.getElementById('floating-tooltip');

        // ==========================================
        // ĐIỀU KHIỂN THU GỌN / MỞ RA THANH CÔNG CỤ (SIDEBAR)
        // ==========================================
        function toggleSidebar(forceOpen) {
            const sidebar = document.getElementById('app-sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');
            const btnText = document.getElementById('toggle-taskbar-text');
            const isMobile = window.innerWidth <= 900;

            let willCollapse;
            if (typeof forceOpen === 'boolean') {
                willCollapse = !forceOpen;
            } else {
                willCollapse = !sidebar.classList.contains('collapsed');
            }

            if (willCollapse) {
                sidebar.classList.add('collapsed');
                backdrop.classList.remove('active');
                if (btnText) btnText.textContent = 'Mở Thanh Công cụ';
            } else {
                sidebar.classList.remove('collapsed');
                if (isMobile) {
                    backdrop.classList.add('active');
                } else {
                    backdrop.classList.remove('active');
                }
                if (btnText) btnText.textContent = 'Thu gọn Công cụ';
            }
        }

        function initResponsiveSidebarState() {
            const sidebar = document.getElementById('app-sidebar');
            const btnText = document.getElementById('toggle-taskbar-text');
            if (window.innerWidth <= 900) {
                sidebar.classList.add('collapsed');
                if (btnText) btnText.textContent = 'Mở Thanh Công cụ';
            } else {
                sidebar.classList.remove('collapsed');
                if (btnText) btnText.textContent = 'Thu gọn Công cụ';
            }
        }

        window.addEventListener('resize', () => {
            const sidebar = document.getElementById('app-sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');
            if (window.innerWidth > 900) {
                backdrop.classList.remove('active');
            } else if (!sidebar.classList.contains('collapsed')) {
                backdrop.classList.add('active');
            }
        });

        function setQuickFilter(keyword) {
            const nameInput = document.getElementById('filter-name');
            if (nameInput) nameInput.value = keyword;
            document.querySelectorAll('.filter-pill').forEach(el => {
                if ((keyword === '' && el.id === 'pill-all') || (keyword !== '' && el.textContent.includes(keyword))) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });
            renderMainWorkspace();
        }

        function resetAllFilters() {
            document.getElementById('filter-name').value = '';
            document.getElementById('filter-concept').value = '';
            document.getElementById('filter-symbol').value = '';
            document.getElementById('filter-status').value = 'Tất cả';
            setQuickFilter('');
        }

        function escapeHtml(str) {
            return String(str || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }

        function showToast(msg) {
            const box = document.getElementById('toast-box');
            box.textContent = msg;
            box.style.display = 'block';
            setTimeout(() => { box.style.display = 'none'; }, 3200);
        }

        function fileToBase64(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });
        }

        async function fetchModels() {
            const res = await fetch('/api/models');
            const data = await res.json();
            if (data.ok) {
                modelsData = data.models || [];
                if (data.github && data.github.enabled) {
                    document.getElementById('github-status-text').innerHTML =
                        `🟢 <b>GitHub Auto-Sync:</b> <code>${escapeHtml(data.github.repo)}</code> (<code>${escapeHtml(data.github.branch)}</code>)`;
                }
                renderMainWorkspace();
                if (selectedModelId && selectedDeviceId && document.getElementById('view-device-detail').style.display !== 'none') {
                    renderDeviceDetailView();
                }
            }
        }

        // ==========================================
        // RENDER LƯỚI THẺ MÔ HÌNH THEO MẪU TECH-BROWN DASHBOARD
        // ==========================================
        function renderMainWorkspace() {
            document.getElementById('total-models-count').textContent = modelsData.length;
            const container = document.getElementById('workspace-container');

            if (!modelsData.length) {
                container.innerHTML = `<div class="info-alert">ℹ️ Chưa có dữ liệu, hãy tạo mục đầu tiên</div>`;
                return;
            }

            const qName = (document.getElementById('filter-name').value || '').toLowerCase();
            const qConcept = (document.getElementById('filter-concept').value || '').toLowerCase();
            const qSymbol = (document.getElementById('filter-symbol').value || '').toLowerCase();
            const qStatus = document.getElementById('filter-status').value;

            const filtered = modelsData.filter(m => {
                const devs = m.devices || [];
                const allNames = (m.title || '') + ' ' + devs.map(d => d.name || '').join(' ');
                const allConcepts = (m.concept || '') + ' ' + devs.map(d => d.concept || '').join(' ');
                const allSymbols = (m.symbol || '') + ' ' + devs.map(d => d.symbol || '').join(' ');

                const matchName = !qName || allNames.toLowerCase().includes(qName);
                const matchConcept = !qConcept || allConcepts.toLowerCase().includes(qConcept);
                const matchSymbol = !qSymbol || allSymbols.toLowerCase().includes(qSymbol);
                const matchStatus = qStatus === 'Tất cả' || m.status === qStatus;
                return matchName && matchConcept && matchSymbol && matchStatus;
            });

            if (!filtered.length) {
                container.innerHTML = `<div class="info-alert">🔍 Không tìm thấy Mô hình hoặc Thiết bị nào khớp với bộ lọc hiện tại.</div>`;
                return;
            }

            let html = `<div class="models-grid">`;
            filtered.forEach(model => {
                const statusBadge = model.status === 'completed'
                    ? `<span class="status-pill-completed">〰 Completed</span>`
                    : `<span class="status-pill-pending">⏳ Pending</span>`;

                const devs = model.devices || [];
                const devBadgesHtml = devs.map(d => {
                    const label = d.symbol ? `${d.symbol} (${d.name})` : `${d.name} (không ký hiệu)`;
                    return `<span class="copper-device-badge"
                                  title="${escapeHtml(d.name)}: ${escapeHtml(d.concept)}"
                                  onclick="navigateToDeviceDetail('${model.id}', '${d.device_id}', '${escapeHtml(d.symbol || '')}')">
                                ${escapeHtml(label)}
                            </span>`;
                }).join('');

                // Khung sơ đồ thu nhỏ (Schematic Strip) mang phong cách mẫu Hình 1.1
                const miniSchematicSvg = `
                <div class="card-schematic-preview" onclick="openModelModal('${model.id}')" title="Nhấn để mở Bản vẽ Kỹ thuật tương tác">
                    <svg viewBox="0 0 360 54" width="100%" height="46" xmlns="http://www.w3.org/2000/svg">
                        <line x1="25" y1="27" x2="95" y2="27" stroke="#d97706" stroke-width="1.5"/>
                        <circle cx="25" cy="27" r="11" fill="none" stroke="#fbbf24" stroke-width="1.6"/>
                        <text x="25" y="31" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="9" fill="#fde68a">${escapeHtml(model.symbol || 'ĐĐT')}</text>
                        <rect x="95" y="19" width="38" height="16" fill="rgba(245,158,11,0.18)" stroke="#f59e0b" stroke-width="1.5" rx="2"/>
                        <line x1="133" y1="27" x2="195" y2="27" stroke="#d97706" stroke-width="1.5"/>
                        <circle cx="195" cy="27" r="3.5" fill="#fbbf24"/>
                        <line x1="195" y1="27" x2="255" y2="27" stroke="#d97706" stroke-width="1.5"/>
                        <rect x="255" y="19" width="38" height="16" fill="rgba(245,158,11,0.18)" stroke="#f59e0b" stroke-width="1.5" rx="2"/>
                        <line x1="293" y1="27" x2="340" y2="27" stroke="#d97706" stroke-width="1.5"/>
                        <circle cx="340" cy="27" r="4" fill="#34d399"/>
                    </svg>
                </div>`;

                html += `
                <div class="glass-card">
                    <div>
                        <div class="card-top-bar">
                            <div class="card-copper-icon" title="Mã mô hình: ${escapeHtml(model.symbol || 'N/A')}">❖</div>
                            ${statusBadge}
                        </div>

                        <h3 class="card-model-title" onclick="openModelModal('${model.id}')">
                            ${escapeHtml(model.title)}
                        </h3>

                        ${miniSchematicSvg}

                        <div class="card-meta-list">
                            <div class="card-meta-row">
                                <span class="card-meta-icon">◈</span>
                                <span><b>Mã ký hiệu:</b> <code>${escapeHtml(model.symbol || 'N/A')}</code> &bull; <b>Phân loại:</b> ${escapeHtml(model.category)}</span>
                            </div>
                            <div class="card-meta-row">
                                <span class="card-meta-icon">📖</span>
                                <span style="white-space:pre-line;"><b>Khái niệm:</b> ${escapeHtml(model.concept)}</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div class="devices-section-label">devices (${devs.length} phần tử / khái niệm — nhấn để xem chi tiết)</div>
                        <div class="device-badges-wrap">
                            ${devBadgesHtml || '<span style="font-size:12.5px; color:var(--text-muted);">Chưa có thiết bị</span>'}
                        </div>

                        <div class="divider"></div>
                        <div class="card-actions-grid">
                            <button class="btn btn-primary" onclick="openModelModal('${model.id}')">🔍 Mở Sơ đồ</button>
                            <button class="btn btn-secondary" onclick="openHotspotModal('${model.id}')">🎯 Khoanh vùng</button>
                            <button class="btn btn-secondary" onclick="openCrudModal('${model.id}')">✏️ Sửa</button>
                            <button class="btn btn-secondary" onclick="deleteModel('${model.id}')">🗑️ Xóa</button>
                        </div>
                    </div>
                </div>`;
            });
            html += `</div>`;
            container.innerHTML = html;
        }

        // ==========================================
        // BẢN VẼ KỸ THUẬT SVG GỐC (HÌNH 1.1, 1.2, 1.3, 1.4, 1.7) - GIỮ NGUYÊN 100% CẤU TRÚC
        // ==========================================
        function getSvgMarkup(model) {
            if (model.diagram_type === 'fig_1_1') {
                return `
                <div class="diagram-box">
                    <svg viewBox="0 0 650 330" width="100%" height="310" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <marker id="arrow-h11" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                                <path d="M 0 1 L 10 5 L 0 9 z" fill="#1c1109"/>
                            </marker>
                        </defs>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h11-daydan" data-sym="Dây dẫn" data-name="Dây dẫn">
                            <path d="M 160 115 L 160 65 L 480 65 L 480 120 M 480 200 L 480 255 L 160 255 L 160 205" fill="none" stroke="transparent" stroke-width="24"/>
                            <path class="wire-path" d="M 160 115 L 160 65 L 480 65 L 480 120 M 480 200 L 480 255 L 160 255 L 160 205" fill="none" stroke="#1c1109" stroke-width="2.6"/>
                            <text x="315" y="25" font-family="Times New Roman, serif" font-size="20" fill="#1c1109">Dây dẫn</text>
                            <line x1="340" y1="32" x2="318" y2="61" stroke="#1c1109" stroke-width="2" marker-end="url(#arrow-h11)"/>
                        </g>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h11-nguon" data-sym="Nguồn" data-name="Nguồn điện">
                            <circle class="shape-elem" cx="160" cy="160" r="45" fill="#fffdf9" stroke="#1c1109" stroke-width="2.6"/>
                            <text x="160" y="166" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">Nguồn</text>
                        </g>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h11-tai" data-sym="Tải" data-name="Phụ tải (Tải)">
                            <rect x="420" y="115" width="90" height="90" fill="transparent"/>
                            <rect class="shape-elem" x="466" y="120" width="28" height="80" fill="#fffdf9" stroke="#1c1109" stroke-width="5"/>
                            <text x="453" y="168" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">Tải</text>
                        </g>
                        <text x="325" y="305" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="19" fill="#1c1109">
                            Hình 1.1 Mô hình mạch điện
                        </text>
                    </svg>
                </div>`;
            } else if (model.diagram_type === 'fig_1_2') {
                return `
                <div class="diagram-box">
                    <svg viewBox="0 0 700 370" width="100%" height="350" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <marker id="arrow-h12" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
                                <path d="M 0 1 L 10 5 L 0 9 z" fill="#1c1109"/>
                            </marker>
                        </defs>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h12-daydan" data-sym="Dây dẫn" data-name="Dây dẫn nối mạch">
                            <path d="M 140 162 L 140 60 L 215 60 M 285 60 L 350 60 M 350 60 L 415 60 M 485 60 L 560 60 L 560 162 M 140 206 L 140 285 L 350 285 M 560 206 L 560 285 L 350 285 M 350 60 L 350 155 M 350 225 L 350 285" fill="none" stroke="transparent" stroke-width="20"/>
                            <path class="wire-path" d="M 140 162 L 140 60 L 215 60 M 285 60 L 350 60 M 350 60 L 415 60 M 485 60 L 560 60 L 560 162 M 140 206 L 140 285 L 350 285 M 560 206 L 560 285 L 350 285 M 350 60 L 350 155 M 350 225 L 350 285" fill="none" stroke="#1c1109" stroke-width="2.4"/>
                        </g>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h12-nguon" data-sym="E1, E2" data-name="Nguồn điện (E1, E2)">
                            <circle class="shape-elem" cx="140" cy="184" r="22" fill="#fffdf9" stroke="#1c1109" stroke-width="2.4"/>
                            <line x1="140" y1="201" x2="140" y2="168" stroke="#1c1109" stroke-width="2" marker-end="url(#arrow-h12)"/>
                            <text x="110" y="191" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">E1</text>
                            <circle class="shape-elem" cx="560" cy="184" r="22" fill="#fffdf9" stroke="#1c1109" stroke-width="2.4"/>
                            <line x1="560" y1="201" x2="560" y2="168" stroke="#1c1109" stroke-width="2" marker-end="url(#arrow-h12)"/>
                            <text x="530" y="191" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">E2</text>
                        </g>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h12-tai" data-sym="R1, R2, R3" data-name="Phụ tải / Điện trở (R1, R2, R3)">
                            <rect class="shape-elem" x="215" y="49" width="70" height="22" fill="#fffdf9" stroke="#1c1109" stroke-width="2.4"/>
                            <text x="250" y="100" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">R<tspan dy="5" font-size="15">1</tspan></text>
                            <rect class="shape-elem" x="415" y="49" width="70" height="22" fill="#fffdf9" stroke="#1c1109" stroke-width="2.4"/>
                            <text x="450" y="100" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">R<tspan dy="5" font-size="15">2</tspan></text>
                            <rect class="shape-elem" x="339" y="155" width="22" height="70" fill="#fffdf9" stroke="#1c1109" stroke-width="2.4"/>
                            <text x="331" y="196" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">R<tspan dy="5" font-size="15">3</tspan></text>
                        </g>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h12-nhanh" data-sym="Nhánh (I1, I2, I3)" data-name="Nhánh mạch điện (Nhánh 1, Nhánh 2, Nhánh 3)">
                            <rect x="205" y="105" width="90" height="52" fill="transparent"/>
                            <line class="wire-path" x1="215" y1="118" x2="285" y2="118" stroke="#1c1109" stroke-width="2.2" marker-end="url(#arrow-h12)"/>
                            <text x="250" y="146" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">I<tspan dy="5" font-size="15">1</tspan></text>
                            <rect x="405" y="105" width="90" height="52" fill="transparent"/>
                            <line class="wire-path" x1="415" y1="118" x2="485" y2="118" stroke="#1c1109" stroke-width="2.2" marker-end="url(#arrow-h12)"/>
                            <text x="450" y="146" text-anchor="middle" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">I<tspan dy="5" font-size="15">2</tspan></text>
                            <rect x="268" y="150" width="45" height="80" fill="transparent"/>
                            <line class="wire-path" x1="298" y1="155" x2="298" y2="225" stroke="#1c1109" stroke-width="2.2" marker-end="url(#arrow-h12)"/>
                            <text x="290" y="198" text-anchor="end" font-family="Times New Roman, serif" font-size="21" fill="#1c1109">I<tspan dy="5" font-size="15">3</tspan></text>
                        </g>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h12-nut" data-sym="Nút A, Nút B" data-name="Nút mạch điện (Nút A, Nút B)">
                            <circle cx="350" cy="60" r="20" fill="transparent"/>
                            <circle class="node-elem" cx="350" cy="60" r="6.5" fill="#1c1109"/>
                            <text x="350" y="36" text-anchor="middle" font-family="Times New Roman, serif" font-size="22" font-weight="bold" fill="#1c1109">A</text>
                            <circle cx="350" cy="285" r="20" fill="transparent"/>
                            <circle class="node-elem" cx="350" cy="285" r="6.5" fill="#1c1109"/>
                            <text x="350" y="320" text-anchor="middle" font-family="Times New Roman, serif" font-size="22" font-weight="bold" fill="#1c1109">B</text>
                        </g>
                        <text x="350" y="355" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="19" fill="#1c1109">
                            Hình 1.2 Kết cấu hình học của mạch điện
                        </text>
                    </svg>
                </div>`;
            } else if (model.diagram_type === 'fig_1_3') {
                return `
                <div class="diagram-box">
                    <svg viewBox="0 0 650 230" width="100%" height="220" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <marker id="arrow-h13" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
                                <path d="M 0 1 L 10 5 L 0 9 z" fill="#1c1109"/>
                            </marker>
                        </defs>
                        <!-- Nhánh cơ sở a - R - b -->
                        <line x1="120" y1="85" x2="265" y2="85" stroke="#1c1109" stroke-width="2.4"/>
                        <line x1="375" y1="85" x2="530" y2="85" stroke="#1c1109" stroke-width="2.4"/>
                        <circle cx="120" cy="85" r="5" fill="#1c1109"/>
                        <circle cx="530" cy="85" r="5" fill="#1c1109"/>
                        <text x="115" y="70" text-anchor="middle" font-family="Times New Roman, serif" font-size="23" fill="#1c1109">a</text>
                        <text x="535" y="70" text-anchor="middle" font-family="Times New Roman, serif" font-size="23" fill="#1c1109">b</text>
                        <rect x="265" y="72" width="110" height="26" fill="#fffdf9" stroke="#1c1109" stroke-width="2.4"/>
                        <text x="320" y="62" text-anchor="middle" font-family="Times New Roman, serif" font-size="23" fill="#1c1109">R</text>

                        <!-- Hotspot: Dòng điện i -->
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h13-dongdien" data-sym="i" data-name="Dòng điện (i)">
                            <rect x="155" y="42" width="85" height="58" fill="transparent"/>
                            <line class="wire-path" x1="170" y1="85" x2="220" y2="85" stroke="#1c1109" stroke-width="2.6" marker-end="url(#arrow-h13)"/>
                            <text x="195" y="68" text-anchor="middle" font-family="Times New Roman, serif" font-size="24" fill="#1c1109">i</text>
                        </g>

                        <!-- Hotspot: Điện áp u_ab -->
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h13-dienap" data-sym="u_ab" data-name="Điện áp (u_ab)">
                            <rect x="215" y="105" width="210" height="55" fill="transparent"/>
                            <text x="320" y="128" text-anchor="middle" font-family="Times New Roman, serif" font-size="23" fill="#1c1109">
                                u<tspan dy="5" font-size="16">ab</tspan>
                            </text>
                            <line class="wire-path" x1="230" y1="145" x2="410" y2="145" stroke="#1c1109" stroke-width="2.4" marker-end="url(#arrow-h13)"/>
                        </g>

                        <text x="325" y="200" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="20" fill="#1c1109">
                            Hình 1.3 Dòng điện và điện áp
                        </text>
                    </svg>
                </div>`;
            } else if (model.diagram_type === 'fig_1_4') {
                return `
                <div class="diagram-box">
                    <svg viewBox="0 0 650 250" width="100%" height="240" xmlns="http://www.w3.org/2000/svg">
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h14-dientro" data-sym="R" data-name="Điện trở (R) - Nhấn để mở Bảng màu & Mô hình hỏi đáp trị số">
                            <rect x="145" y="30" width="360" height="155" fill="transparent"/>
                            <!-- Ký hiệu 1: Điện trở dạng răng cưa -->
                            <path class="wire-path" d="M 165 72 L 265 72 L 274 56 L 288 88 L 302 56 L 316 88 L 330 56 L 344 88 L 353 72 L 485 72" fill="none" stroke="#1c1109" stroke-width="3.2" stroke-linejoin="round"/>
                            <!-- Ký hiệu 2: Điện trở dạng hình chữ nhật -->
                            <line class="wire-path" x1="165" y1="145" x2="265" y2="145" stroke="#1c1109" stroke-width="3.2"/>
                            <rect class="shape-elem" x="265" y="130" width="120" height="30" fill="#fffdf9" stroke="#1c1109" stroke-width="3.2"/>
                            <line class="wire-path" x1="385" y1="145" x2="485" y2="145" stroke="#1c1109" stroke-width="3.2"/>
                        </g>
                        <text x="325" y="220" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="20" fill="#1c1109">
                            Hình 1.4 Ký hiệu của điện trở
                        </text>
                    </svg>
                </div>`;
            } else if (model.diagram_type === 'fig_1_7') {
                return `
                <div class="diagram-box">
                    <svg viewBox="0 0 650 250" width="100%" height="240" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <marker id="arrow-h17" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
                                <path d="M 0 1 L 10 5 L 0 9 z" fill="#1c1109"/>
                            </marker>
                        </defs>
                        <g class="svg-hotspot" data-model-id="${model.id}" data-dev-id="h17-cuonday" data-sym="L" data-name="Cuộn dây (L) - Nhấn để mở Bảng màu & Bảng sai số điện cảm">
                            <rect x="145" y="25" width="360" height="165" fill="transparent"/>
                            <!-- Dây dẫn và mũi tên dòng điện i -->
                            <line class="wire-path" x1="165" y1="95" x2="245" y2="95" stroke="#1c1109" stroke-width="3"/>
                            <path d="M 192 86 L 206 95 L 192 104" fill="none" stroke="#1c1109" stroke-width="2.6"/>
                            <text x="196" y="78" text-anchor="middle" font-family="Times New Roman, serif" font-size="25" fill="#1c1109">i</text>
                            <!-- 4 vòng cung cuộn cảm L -->
                            <path class="wire-path" d="M 245 95 A 20 18 0 0 1 285 95 A 20 18 0 0 1 325 95 A 20 18 0 0 1 365 95 A 20 18 0 0 1 405 95" fill="none" stroke="#1c1109" stroke-width="3.2"/>
                            <line class="wire-path" x1="405" y1="95" x2="485" y2="95" stroke="#1c1109" stroke-width="3"/>
                            <text x="325" y="56" text-anchor="middle" font-family="Times New Roman, serif" font-size="27" fill="#1c1109">L</text>
                            <!-- Mũi tên điện áp u_L -->
                            <line class="wire-path" x1="168" y1="128" x2="480" y2="128" stroke="#1c1109" stroke-width="3" marker-end="url(#arrow-h17)"/>
                            <text x="325" y="166" text-anchor="middle" font-family="Times New Roman, serif" font-size="26" fill="#1c1109">
                                u<tspan dy="6" font-size="18">L</tspan>
                            </text>
                        </g>
                        <text x="325" y="220" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="20" fill="#1c1109">
                            Hình 1.7 Ký hiệu của cuộn dây
                        </text>
                    </svg>
                </div>`;
            }
            return '';
        }

        function getCustomDiagramMarkup(model) {
            if (!model.diagram_image) return '';
            const devMap = {};
            (model.devices || []).forEach(d => { devMap[d.device_id] = d; });

            let boxesHtml = '';
            (model.hotspots || []).forEach(hs => {
                const dev = devMap[hs.device_id] || {};
                const devName = dev.name || hs.name || 'Thiết bị';
                const devSym = dev.symbol || hs.symbol || '';
                const badge = devSym || devName;
                boxesHtml += `
                <div class="custom-hs-box"
                     data-model-id="${model.id}"
                     data-dev-id="${escapeHtml(hs.device_id)}"
                     data-sym="${escapeHtml(devSym)}"
                     data-name="${escapeHtml(devName)}"
                     style="left:${hs.x}%; top:${hs.y}%; width:${hs.w}%; height:${hs.h}%;">
                    <span class="hs-tag">${escapeHtml(badge)}</span>
                </div>`;
            });

            return `
            <h4 style="margin:16px 0 8px 0; font-family:var(--font-display); color:var(--amber-light);">🖼️ Sơ đồ Mô hình Tùy chỉnh (Tương tác qua vùng đã khoanh)</h4>
            <div class="custom-diagram-wrapper">
                <img src="${model.diagram_image}" alt="Sơ đồ mô hình" />
                ${boxesHtml}
            </div>`;
        }

        function bindDiagramHotspotEvents(container) {
            const nodes = container.querySelectorAll('.svg-hotspot, .custom-hs-box');
            nodes.forEach(node => {
                node.addEventListener('mousemove', (e) => {
                    if (window.innerWidth <= 900) return;
                    const name = node.getAttribute('data-name');
                    tooltipEl.innerHTML = `⚡ <b>${escapeHtml(name)}</b> <span style="color:#fbbf24;font-size:12px;">(Nhấn để xem chi tiết)</span>`;
                    tooltipEl.style.display = 'block';
                    let leftPos = e.clientX + 14;
                    let topPos = e.clientY - 36;
                    if (leftPos + 290 > window.innerWidth) leftPos = e.clientX - 270;
                    if (topPos < 8) topPos = e.clientY + 18;
                    tooltipEl.style.left = leftPos + 'px';
                    tooltipEl.style.top = topPos + 'px';
                });
                node.addEventListener('mouseleave', () => {
                    tooltipEl.style.display = 'none';
                });
                node.addEventListener('click', (e) => {
                    e.stopPropagation();
                    tooltipEl.style.display = 'none';
                    const modelId = node.getAttribute('data-model-id');
                    const devId = node.getAttribute('data-dev-id');
                    const sym = node.getAttribute('data-sym');
                    navigateToDeviceDetail(modelId, devId, sym);
                });
            });
        }

        // ==========================================
        // MODAL SƠ ĐỒ MÔ HÌNH & KÝ HIỆU THIẾT BỊ
        // ==========================================
        function openModelModal(modelId) {
            const model = modelsData.find(m => m.id === modelId);
            if (!model) return;

            const devs = model.devices || [];
            const symbolDevs = devs.filter(d => (d.symbol || '').trim() !== '');
            const nonSymbolDevs = devs.filter(d => (d.symbol || '').trim() === '');

            let symButtonsHtml = '';
            if (symbolDevs.length) {
                symButtonsHtml += `
                <div class="glass-card" style="margin-top:16px;">
                    <h4 style="margin:0 0 12px 0; font-family:var(--font-display); color:var(--amber-light);">⚡ Các Ký hiệu Thiết bị trên Mô hình (Chạm trực tiếp trên bản vẽ hoặc chọn Badge bên dưới)</h4>
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap:10px;">
                        ${symbolDevs.map(d => `
                            <button class="btn btn-primary" title="Tên thiết bị: ${escapeHtml(d.name)}"
                                    onclick="navigateToDeviceDetail('${model.id}', '${d.device_id}', '${escapeHtml(d.symbol)}')">
                                🔣 ${escapeHtml(d.symbol)} — ${escapeHtml(d.name)}
                            </button>
                        `).join('')}
                    </div>
                </div>`;
            }

            let nonSymHtml = '';
            if (nonSymbolDevs.length) {
                nonSymHtml += `
                <div class="glass-card" style="margin-top:16px;">
                    <h4 style="margin:0 0 10px 0; font-family:var(--font-display); color:var(--amber-light);">📘 Khái niệm & Công thức thuộc mô hình (Không có ký hiệu riêng trên hình)</h4>
                    ${nonSymbolDevs.map(d => `
                        <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid rgba(180,83,9,0.25);">
                            <div style="flex:1; min-width:210px;">
                                <div style="white-space:pre-line;"><b style="color:var(--amber-pale);">${escapeHtml(d.name)}:</b> ${escapeHtml(d.concept)}</div>
                                <div style="font-size:12.5px; color:var(--text-muted); margin-top:4px; white-space:pre-line;">${escapeHtml(d.details)}</div>
                            </div>
                            <button class="btn btn-secondary" style="white-space:nowrap;"
                                    onclick="navigateToDeviceDetail('${model.id}', '${d.device_id}', '')">
                                📄 Xem khái niệm & công thức
                            </button>
                        </div>
                    `).join('')}
                </div>`;
            }

            const body = document.getElementById('modal-model-body');
            body.innerHTML = `
                <h2 style="margin:0 0 6px 0; font-family:var(--font-display); color:var(--amber-light); padding-right:36px;">📐 ${escapeHtml(model.title)} (<code>${escapeHtml(model.symbol || 'N/A')}</code>)</h2>
                <div style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">
                    Phân loại: ${escapeHtml(model.category)} | Trạng thái: <b style="color:var(--emerald-text);">${escapeHtml(model.status)}</b>
                </div>
                <p style="margin:0 0 14px 0; line-height:1.6; color:var(--text-secondary); white-space:pre-line;"><b>Khái niệm mô hình:</b> ${escapeHtml(model.concept)}</p>
                <div class="divider"></div>
                <p style="font-size:13.5px; color:var(--amber-pale); margin:12px 0; line-height:1.5;">
                    💡 <i>Hướng dẫn: <b>Di chuột hoặc chạm</b> trực tiếp vào các ký hiệu trên bản vẽ kỹ thuật nền Cream-Sand để xem hiệu ứng phát sáng Hotspot và chuyển sang trang nội dung chi tiết.</i>
                </p>
                ${getSvgMarkup(model)}
                ${getCustomDiagramMarkup(model)}
                ${symButtonsHtml}
                ${nonSymHtml}
            `;

            bindDiagramHotspotEvents(body);
            document.getElementById('modal-model').classList.add('active');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
            tooltipEl.style.display = 'none';
        }

        // ==========================================
        // VISUAL HOTSPOT EDITOR MODAL (HỖ TRỢ CHUỘT & CẢM ỨNG DI ĐỘNG)
        // ==========================================
        function openHotspotModal(modelId) {
            const model = modelsData.find(m => m.id === modelId);
            if (!model) return;
            editorModelId = model.id;
            editorHotspots = JSON.parse(JSON.stringify(model.hotspots || []));

            const devs = model.devices || [];
            const body = document.getElementById('modal-hotspot-body');

            body.innerHTML = `
                <h2 style="margin:0 0 12px 0; font-family:var(--font-display); color:var(--amber-light); padding-right:36px;">🎯 Visual Hotspot Editor — ${escapeHtml(model.title)}</h2>
                <div class="glass-card" style="margin-bottom:16px;">
                    <h4 style="margin:0 0 10px 0; font-family:var(--font-display); color:var(--amber-pale);">🖼️ Bước 1: Tải ảnh sơ đồ mô hình (hoặc dán URL ảnh)</h4>
                    <div class="form-grid-2">
                        <div>
                            <label>Chọn file ảnh sơ đồ (.png, .jpg, .webp)</label>
                            <input type="file" id="hs-upload-file" accept="image/*" />
                        </div>
                        <div>
                            <label>Hoặc nhập URL ảnh sơ đồ</label>
                            <input type="text" id="hs-upload-url" value="${model.diagram_image && model.diagram_image.startsWith('http') ? escapeHtml(model.diagram_image) : ''}" placeholder="https://example.com/circuit.png" />
                        </div>
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:10px;">
                        <button class="btn btn-primary" style="flex:1; min-width:180px;" onclick="updateModelDiagramImage()">📸 Cập nhật ảnh sơ đồ</button>
                        ${model.diagram_image ? `<button class="btn btn-secondary" onclick="clearModelDiagramImage()">🗑️ Xóa ảnh sơ đồ tùy chỉnh</button>` : ''}
                    </div>
                </div>

                ${!model.diagram_image ? `
                    <div class="info-alert">
                        💡 Mô hình này chưa có ảnh sơ đồ tùy chỉnh. Hãy tải lên 1 ảnh sơ đồ ở <b>Bước 1</b> phía trên để bắt đầu kéo khoanh vùng đánh dấu ký hiệu bằng tay
                        (Các bản vẽ SVG gốc vẫn luôn được giữ nguyên 100%).
                    </div>
                ` : `
                    <div class="glass-card">
                        <h4 style="margin:0 0 10px 0; font-family:var(--font-display); color:var(--amber-pale);">🎯 Bước 2: Chọn Thiết bị & Kéo trên ảnh sơ đồ để khoanh vùng ký hiệu</h4>
                        <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px; align-items:center;">
                            <select id="hs-device-select" style="flex:1; min-width:200px;">
                                ${devs.map(d => `<option value="${escapeHtml(d.device_id)}">${d.symbol ? '[' + escapeHtml(d.symbol) + '] ' : '[Không ký hiệu] '}${escapeHtml(d.name)}</option>`).join('')}
                            </select>
                            <button class="btn btn-secondary" onclick="undoHotspot()">↩️ Hoàn tác</button>
                            <button class="btn btn-secondary" onclick="clearAllHotspots()">🗑️ Xóa hết</button>
                            <button class="btn btn-primary" onclick="saveHotspotsToServer()">💾 Lưu vùng khoanh</button>
                        </div>
                        <div class="canvas-stage-wrap">
                            <div id="editor-stage">
                                <img src="${model.diagram_image}" draggable="false" />
                                <div id="editor-boxes-layer"></div>
                                <div id="rubber-band"></div>
                            </div>
                        </div>
                        <div style="margin-top:10px; font-size:12.5px; color:var(--text-muted); display:flex; flex-wrap:wrap; justify-content:space-between; gap:6px;">
                            <span id="hs-count-label">Đã khoanh ${editorHotspots.length} vùng ký hiệu.</span>
                            <span style="color:var(--amber-light);">💡 Kéo chuột hoặc chạm kéo trên ảnh để vẽ khung khoanh vùng</span>
                        </div>
                    </div>
                `}
            `;

            document.getElementById('modal-hotspot').classList.add('active');
            if (model.diagram_image) {
                initHotspotStageEvents(devs);
                renderEditorBoxes();
            }
        }

        function renderEditorBoxes() {
            const layer = document.getElementById('editor-boxes-layer');
            if (!layer) return;
            layer.innerHTML = '';
            editorHotspots.forEach((hs, idx) => {
                const box = document.createElement('div');
                box.className = 'drawn-box';
                box.style.left = hs.x + '%';
                box.style.top = hs.y + '%';
                box.style.width = hs.w + '%';
                box.style.height = hs.h + '%';

                const lbl = document.createElement('div');
                lbl.className = 'drawn-box-label';
                const txt = hs.symbol ? `${hs.symbol} (${hs.name})` : hs.name;
                lbl.innerHTML = `<span>${escapeHtml(txt)}</span>`;

                const delBtn = document.createElement('span');
                delBtn.className = 'del-hs-btn';
                delBtn.textContent = '✕';
                delBtn.onclick = (e) => {
                    e.stopPropagation();
                    editorHotspots.splice(idx, 1);
                    renderEditorBoxes();
                };
                lbl.appendChild(delBtn);
                box.appendChild(lbl);
                layer.appendChild(box);
            });
            const countLbl = document.getElementById('hs-count-label');
            if (countLbl) countLbl.textContent = `Đã khoanh ${editorHotspots.length} vùng ký hiệu trên sơ đồ.`;
        }

        function initHotspotStageEvents(devs) {
            const stage = document.getElementById('editor-stage');
            const rubber = document.getElementById('rubber-band');
            if (!stage || !rubber) return;

            let isDrawing = false;
            let startX = 0, startY = 0;

            function startDrag(clientX, clientY, target) {
                if (target && target.classList && target.classList.contains('del-hs-btn')) return;
                const rect = stage.getBoundingClientRect();
                isDrawing = true;
                startX = clientX - rect.left;
                startY = clientY - rect.top;
                rubber.style.left = startX + 'px';
                rubber.style.top = startY + 'px';
                rubber.style.width = '0px';
                rubber.style.height = '0px';
                rubber.style.display = 'block';
            }

            function moveDrag(clientX, clientY) {
                if (!isDrawing) return;
                const rect = stage.getBoundingClientRect();
                const curX = Math.max(0, Math.min(clientX - rect.left, rect.width));
                const curY = Math.max(0, Math.min(clientY - rect.top, rect.height));
                rubber.style.left = Math.min(startX, curX) + 'px';
                rubber.style.top = Math.min(startY, curY) + 'px';
                rubber.style.width = Math.abs(curX - startX) + 'px';
                rubber.style.height = Math.abs(curY - startY) + 'px';
            }

            function endDrag(clientX, clientY) {
                if (!isDrawing) return;
                isDrawing = false;
                rubber.style.display = 'none';
                const rect = stage.getBoundingClientRect();
                const curX = Math.max(0, Math.min(clientX - rect.left, rect.width));
                const curY = Math.max(0, Math.min(clientY - rect.top, rect.height));
                const leftPx = Math.min(startX, curX);
                const topPx = Math.min(startY, curY);
                const widthPx = Math.abs(curX - startX);
                const heightPx = Math.abs(curY - startY);
                if (widthPx < 8 || heightPx < 8) return;

                const selId = document.getElementById('hs-device-select').value;
                const devObj = devs.find(d => d.device_id === selId) || devs[0];

                editorHotspots.push({
                    hotspot_id: 'hs-' + Date.now(),
                    device_id: devObj.device_id,
                    symbol: devObj.symbol || '',
                    name: devObj.name || 'Thiết bị',
                    x: Math.round((leftPx / rect.width) * 10000) / 100,
                    y: Math.round((topPx / rect.height) * 10000) / 100,
                    w: Math.round((widthPx / rect.width) * 10000) / 100,
                    h: Math.round((heightPx / rect.height) * 10000) / 100
                });
                renderEditorBoxes();
            }

            stage.onmousedown = (e) => {
                if (e.button !== 0) return;
                startDrag(e.clientX, e.clientY, e.target);
            };
            stage.onmousemove = (e) => moveDrag(e.clientX, e.clientY);
            window.onmouseup = (e) => endDrag(e.clientX, e.clientY);

            stage.ontouchstart = (e) => {
                if (!e.touches || !e.touches[0]) return;
                if (e.target && e.target.classList && e.target.classList.contains('del-hs-btn')) return;
                e.preventDefault();
                startDrag(e.touches[0].clientX, e.touches[0].clientY, e.target);
            };
            stage.ontouchmove = (e) => {
                if (!isDrawing || !e.touches || !e.touches[0]) return;
                e.preventDefault();
                moveDrag(e.touches[0].clientX, e.touches[0].clientY);
            };
            stage.ontouchend = (e) => {
                if (!isDrawing) return;
                const touch = (e.changedTouches && e.changedTouches[0]) ? e.changedTouches[0] : null;
                if (touch) endDrag(touch.clientX, touch.clientY);
            };
        }

        function undoHotspot() {
            editorHotspots.pop();
            renderEditorBoxes();
        }

        function clearAllHotspots() {
            editorHotspots = [];
            renderEditorBoxes();
        }

        async function updateModelDiagramImage() {
            const fileInput = document.getElementById('hs-upload-file');
            const urlInput = document.getElementById('hs-upload-url');
            let imgData = '';
            if (fileInput && fileInput.files && fileInput.files[0]) {
                imgData = await fileToBase64(fileInput.files[0]);
            } else if (urlInput && urlInput.value.trim()) {
                imgData = urlInput.value.trim();
            } else {
                alert('Vui lòng chọn 1 file ảnh hoặc nhập đường dẫn URL ảnh sơ đồ!');
                return;
            }
            const res = await fetch(`/api/models/${editorModelId}/hotspots`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ diagram_image: imgData })
            });
            const data = await res.json();
            if (data.ok) {
                modelsData = data.models;
                showToast('✅ Đã cập nhật ảnh sơ đồ mô hình!');
                openHotspotModal(editorModelId);
            }
        }

        async function clearModelDiagramImage() {
            const res = await fetch(`/api/models/${editorModelId}/hotspots`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ diagram_image: '', hotspots: [] })
            });
            const data = await res.json();
            if (data.ok) {
                modelsData = data.models;
                showToast('🗑️ Đã xóa ảnh sơ đồ tùy chỉnh!');
                openHotspotModal(editorModelId);
            }
        }

        async function saveHotspotsToServer() {
            const res = await fetch(`/api/models/${editorModelId}/hotspots`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hotspots: editorHotspots })
            });
            const data = await res.json();
            if (data.ok) {
                modelsData = data.models;
                showToast(`🎯 Đã lưu ${editorHotspots.length} vùng đánh dấu ký hiệu!`);
                closeModal('modal-hotspot');
                renderMainWorkspace();
            }
        }

        // ==========================================
        // MODULE CHUYÊN BIỆT 1: BẢNG MÀU, VÍ DỤ HÌNH 1.5 & 1.6 VÀ QUIZ ĐIỆN TRỞ (HÌNH 1.4)
        // ==========================================
        function buildResistorLearningSectionHtml() {
            return `
            <div class="divider"></div>
            <div class="glass-card" style="margin-top:18px;">
                <span class="tech-badge">🎨 PHẦN 1: BẢNG MÀU ĐỌC TRỊ SỐ ĐIỆN TRỞ</span>
                <h3 style="margin:8px 0 6px 0; font-family:var(--font-display); color:var(--amber-light);">📊 Bảng quy ước vòng màu Điện trở (3, 4 và 5 vòng màu)</h3>
                <p style="font-size:13.5px; color:var(--text-secondary); margin:0 0 10px 0; line-height:1.55;">
                    - <b>Điện trở 4 vòng màu:</b> Vòng 1 và 2 là chữ số hàng chục và đơn vị; Vòng 3 là hệ số nhân cơ số 10; Vòng 4 là dung sai (sai số).<br/>
                    - <b>Điện trở 5 vòng màu:</b> Vòng 1, 2, 3 là 3 chữ số có nghĩa; Vòng 4 là hệ số nhân cơ số 10; Vòng 5 là dung sai.<br/>
                    - <b>Điện trở 3 vòng màu:</b> Không có vòng màu sai số ở cuối — mặc định dung sai là <b>± 20%</b>.
                </p>
                <div style="overflow-x:auto;">
                    <table class="tech-table">
                        <thead>
                            <tr>
                                <th>Màu</th>
                                <th>Trị số Vạch 1, 2<br/><span style="font-size:12px;font-weight:400;">(Vạch 1, 2, 3 với loại 5 vòng)</span></th>
                                <th>Hệ số Vạch 3<br/><span style="font-size:12px;font-weight:400;">(Vạch 4 với loại 5 vòng)</span></th>
                                <th>Dung sai Vạch 4<br/><span style="font-size:12px;font-weight:400;">(Vạch 5 với loại 5 vòng)</span></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="background:#090d16; color:#ffffff;"><td>Đen</td><td>0</td><td>10<sup>0</sup></td><td>-</td></tr>
                            <tr style="background:#78350f; color:#ffffff;"><td>Nâu</td><td>1</td><td>10<sup>1</sup></td><td>1 %</td></tr>
                            <tr style="background:#dc2626; color:#ffffff;"><td>Đỏ</td><td>2</td><td>10<sup>2</sup></td><td>2%</td></tr>
                            <tr style="background:#ea580c; color:#ffffff;"><td>Cam</td><td>3</td><td>10<sup>3</sup></td><td>-</td></tr>
                            <tr style="background:#facc15; color:#0f172a;"><td>Vàng</td><td>4</td><td>10<sup>4</sup></td><td>-</td></tr>
                            <tr style="background:#16a34a; color:#ffffff;"><td>Xanh lục</td><td>5</td><td>10<sup>5</sup></td><td>0,5%</td></tr>
                            <tr style="background:#0284c7; color:#ffffff;"><td>Xanh lam</td><td>6</td><td>10<sup>6</sup></td><td>-</td></tr>
                            <tr style="background:#7e22ce; color:#ffffff;"><td>Tím</td><td>7</td><td>10<sup>7</sup></td><td>-</td></tr>
                            <tr style="background:#6b7280; color:#ffffff;"><td>Xám</td><td>8</td><td>10<sup>8</sup></td><td>-</td></tr>
                            <tr style="background:#f8fafc; color:#0f172a;"><td>Trắng</td><td>9</td><td>10<sup>9</sup></td><td>-</td></tr>
                            <tr style="background:#fde047; color:#0f172a;"><td>Kim nhũ (Nhũ vàng)</td><td>-</td><td>10<sup>-1</sup></td><td>5 %</td></tr>
                            <tr style="background:#cbd5e1; color:#0f172a;"><td>Ngân nhũ (Nhũ bạc)</td><td>-</td><td>10<sup>-2</sup></td><td>10%</td></tr>
                            <tr style="background:rgba(26,16,9,0.92); color:var(--amber-pale);"><td>Không màu (3 vòng)</td><td>-</td><td>-</td><td>± 20%</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- PHẦN 2: VÍ DỤ BẰNG 2 HÌNH 1.5 VÀ 1.6 -->
            <div class="glass-card" style="margin-top:18px;">
                <span class="tech-badge">📐 PHẦN 2: VÍ DỤ MINH HỌA TRỰC QUAN (HÌNH 1.5 & HÌNH 1.6)</span>
                <h3 style="margin:8px 0 12px 0; font-family:var(--font-display); color:var(--amber-light);">🔍 Ví dụ cách đọc trị số Điện trở 4 vòng màu và 5 vòng màu</h3>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr)); gap:18px;">
                    <!-- HÌNH 1.5 -->
                    <div style="background:rgba(20,12,6,0.75); border:1px solid rgba(217,119,6,0.38); border-radius:10px; padding:14px;">
                        <h4 style="margin:0 0 6px 0; color:var(--amber-light);">1. Cách đọc trị số điện trở 4 vòng màu (Hình 1.5)</h4>
                        <div style="font-size:13.5px; margin-bottom:8px;">
                            <b>Công thức:</b> <code>Trị số = (vòng 1)(vòng 2) × 10^(vòng 3)</code>
                        </div>
                        <div class="diagram-box" style="margin:8px auto;">
                            <svg viewBox="0 0 620 270" width="100%" height="235" xmlns="http://www.w3.org/2000/svg">
                                <defs>
                                    <marker id="arr-fig15" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#0f172a"/>
                                    </marker>
                                </defs>
                                <!-- Dây chân điện trở -->
                                <rect x="70" y="47" width="120" height="8" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>
                                <rect x="430" y="47" width="120" height="8" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>
                                <!-- Thân điện trở -->
                                <rect x="190" y="25" width="240" height="52" fill="#93c5fd" stroke="#1e293b" stroke-width="2"/>
                                <!-- 4 Vòng màu: Đỏ, Tím, Cam, Nhũ vàng -->
                                <rect x="210" y="25" width="18" height="52" fill="#ef4444" stroke="#1e293b" stroke-width="1.5"/>
                                <rect x="255" y="25" width="18" height="52" fill="#d946ef" stroke="#1e293b" stroke-width="1.5"/>
                                <rect x="300" y="25" width="18" height="52" fill="#f97316" stroke="#1e293b" stroke-width="1.5"/>
                                <rect x="380" y="25" width="18" height="52" fill="#facc15" stroke="#1e293b" stroke-width="1.5"/>

                                <!-- Nhãn chỉ vào từng vòng -->
                                <line x1="165" y1="120" x2="215" y2="82" stroke="#0f172a" stroke-width="1.5" marker-end="url(#arr-fig15)"/>
                                <rect x="105" y="122" width="110" height="32" rx="4" fill="#dcfce7"/>
                                <text x="160" y="136" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Vòng số 1</text>
                                <text x="160" y="150" text-anchor="middle" font-size="12" fill="#0f172a">Mầu đỏ</text>

                                <line x1="255" y1="132" x2="264" y2="82" stroke="#0f172a" stroke-width="1.5" marker-end="url(#arr-fig15)"/>
                                <rect x="205" y="134" width="105" height="32" rx="4" fill="#dcfce7"/>
                                <text x="257" y="148" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Vòng số 2</text>
                                <text x="257" y="162" text-anchor="middle" font-size="12" fill="#0f172a">Mầu tím</text>

                                <line x1="365" y1="132" x2="312" y2="82" stroke="#0f172a" stroke-width="1.5" marker-end="url(#arr-fig15)"/>
                                <rect x="320" y="134" width="105" height="32" rx="4" fill="#dcfce7"/>
                                <text x="372" y="148" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Vòng số 3</text>
                                <text x="372" y="162" text-anchor="middle" font-size="12" fill="#0f172a">Mầu cam</text>

                                <line x1="465" y1="118" x2="395" y2="82" stroke="#0f172a" stroke-width="1.5" marker-end="url(#arr-fig15)"/>
                                <rect x="420" y="120" width="110" height="32" rx="4" fill="#dcfce7"/>
                                <text x="475" y="134" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Vòng số 4</text>
                                <text x="475" y="148" text-anchor="middle" font-size="12" fill="#0f172a">Nhũ vàng</text>

                                <!-- Kết quả tính toán -->
                                <line x1="165" y1="156" x2="205" y2="195" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig15)"/>
                                <line x1="255" y1="168" x2="235" y2="195" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig15)"/>
                                <line x1="360" y1="168" x2="295" y2="195" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig15)"/>
                                <line x1="475" y1="154" x2="475" y2="205" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig15)"/>

                                <text x="245" y="212" text-anchor="middle" font-size="19" font-weight="bold" fill="#0f172a">
                                    2  7 × 10<tspan dy="-8" font-size="14">3</tspan>
                                </text>
                                <text x="245" y="232" text-anchor="middle" font-size="18" font-weight="bold" fill="#0f172a">= 27.000 Ω</text>
                                <text x="245" y="250" text-anchor="middle" font-size="18" font-weight="bold" fill="#0f172a">= 27 K Ω</text>
                                <text x="475" y="222" text-anchor="middle" font-size="14" font-weight="bold" fill="#0f172a">Sai số 5%</text>
                                <text x="310" y="267" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="16" fill="#0f172a">
                                    Hình 1.5 Điện trở bốn vòng màu
                                </text>
                            </svg>
                        </div>
                    </div>

                    <!-- HÌNH 1.6 -->
                    <div style="background:rgba(20,12,6,0.75); border:1px solid rgba(217,119,6,0.38); border-radius:10px; padding:14px;">
                        <h4 style="margin:0 0 6px 0; color:var(--amber-light);">2. Cách đọc trị số điện trở 5 vòng màu (Hình 1.6)</h4>
                        <div style="font-size:13.5px; margin-bottom:8px;">
                            <b>Công thức:</b> <code>Trị số = (vòng 1)(vòng 2)(vòng 3) × 10^(vòng 4)</code>
                        </div>
                        <div class="diagram-box" style="margin:8px auto;">
                            <svg viewBox="0 0 620 270" width="100%" height="235" xmlns="http://www.w3.org/2000/svg">
                                <defs>
                                    <marker id="arr-fig16" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#0f172a"/>
                                    </marker>
                                </defs>
                                <!-- Dây chân điện trở -->
                                <rect x="70" y="47" width="120" height="8" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>
                                <rect x="430" y="47" width="120" height="8" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>
                                <!-- Thân điện trở -->
                                <rect x="190" y="25" width="240" height="52" fill="#93c5fd" stroke="#1e293b" stroke-width="2"/>
                                <!-- 5 Vòng màu: Đỏ, Tím, Vàng, Đỏ, Nâu -->
                                <rect x="206" y="25" width="16" height="52" fill="#ef4444" stroke="#1e293b" stroke-width="1.5"/>
                                <rect x="246" y="25" width="16" height="52" fill="#d946ef" stroke="#1e293b" stroke-width="1.5"/>
                                <rect x="286" y="25" width="16" height="52" fill="#facc15" stroke="#1e293b" stroke-width="1.5"/>
                                <rect x="326" y="25" width="16" height="52" fill="#ef4444" stroke="#1e293b" stroke-width="1.5"/>
                                <rect x="382" y="25" width="16" height="52" fill="#78350f" stroke="#1e293b" stroke-width="1.5"/>

                                <!-- Nhãn chỉ vào từng vòng -->
                                <line x1="130" y1="115" x2="210" y2="82" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig16)"/>
                                <rect x="75" y="117" width="95" height="30" rx="4" fill="#dcfce7"/>
                                <text x="122" y="130" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Vòng số 1</text>
                                <text x="122" y="143" text-anchor="middle" font-size="11.5" fill="#0f172a">Mầu đỏ</text>

                                <line x1="220" y1="130" x2="252" y2="82" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig16)"/>
                                <rect x="175" y="132" width="90" height="30" rx="4" fill="#dcfce7"/>
                                <text x="220" y="145" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Vòng số 2</text>
                                <text x="220" y="158" text-anchor="middle" font-size="11.5" fill="#0f172a">Mầu tím</text>

                                <line x1="312" y1="130" x2="294" y2="82" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig16)"/>
                                <rect x="270" y="132" width="90" height="30" rx="4" fill="#dcfce7"/>
                                <text x="315" y="145" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Vòng số 3</text>
                                <text x="315" y="158" text-anchor="middle" font-size="11.5" fill="#0f172a">Mầu vàng</text>

                                <line x1="408" y1="130" x2="336" y2="82" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig16)"/>
                                <rect x="366" y="132" width="90" height="30" rx="4" fill="#dcfce7"/>
                                <text x="411" y="145" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Vòng số 4</text>
                                <text x="411" y="158" text-anchor="middle" font-size="11.5" fill="#0f172a">Mầu đỏ</text>

                                <line x1="495" y1="115" x2="394" y2="82" stroke="#0f172a" stroke-width="1.4" marker-end="url(#arr-fig16)"/>
                                <rect x="455" y="117" width="95" height="30" rx="4" fill="#dcfce7"/>
                                <text x="502" y="130" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Vòng số 5</text>
                                <text x="502" y="143" text-anchor="middle" font-size="11.5" fill="#0f172a">Mầu nâu</text>

                                <!-- Kết quả tính toán -->
                                <text x="255" y="212" text-anchor="middle" font-size="18.5" font-weight="bold" fill="#0f172a">
                                    2  7  4 × 10<tspan dy="-8" font-size="14">2</tspan>
                                </text>
                                <text x="255" y="232" text-anchor="middle" font-size="17.5" font-weight="bold" fill="#0f172a">= 27400 Ω</text>
                                <text x="255" y="250" text-anchor="middle" font-size="17.5" font-weight="bold" fill="#0f172a">= 27,4 KΩ</text>
                                <text x="502" y="215" text-anchor="middle" font-size="14" font-weight="bold" fill="#0f172a">Sai số 1%</text>
                                <text x="310" y="267" text-anchor="middle" font-family="Times New Roman, serif" font-style="italic" font-size="16" fill="#0f172a">
                                    Hình 1.6 Điện trở 5 vòng màu
                                </text>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PHẦN 3: MÔ HÌNH HỎI ĐÁP TRỊ SỐ ĐIỆN TRỞ -->
            <div class="glass-card" style="margin-top:18px; border-color: var(--amber-cyber);">
                <span class="tech-badge">🎯 PHẦN 3: MÔ HÌNH HỎI ĐÁP (QUIZ) ĐỌC TRỊ SỐ ĐIỆN TRỞ</span>
                <h3 style="margin:8px 0 6px 0; font-family:var(--font-display); color:var(--amber-light);">🧠 Luyện tập đọc trị số Điện trở 3, 4 hoặc 5 vòng màu</h3>
                <p style="font-size:13.5px; color:var(--text-secondary); margin:0 0 12px 0; line-height:1.55;">
                    Chọn số lượng vòng màu (<b>3 vòng</b>, <b>4 vòng</b> hoặc <b>5 vòng</b>). Hệ thống sẽ tự động sinh màu ngẫu nhiên cho các vòng màu trên thân điện trở.
                    Hãy tính trị số và chọn sai số tương ứng rồi nhấn <b>Kiểm tra kết quả</b>!
                </p>

                <div style="display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin-bottom:14px;">
                    <span style="font-size:13.5px; font-weight:600; color:var(--amber-pale);">Chọn loại điện trở:</span>
                    <button id="btn-band-3" class="btn btn-secondary" onclick="generateResistorQuiz(3)">3 Vòng màu</button>
                    <button id="btn-band-4" class="btn btn-secondary" onclick="generateResistorQuiz(4)">4 Vòng màu</button>
                    <button id="btn-band-5" class="btn btn-secondary" onclick="generateResistorQuiz(5)">5 Vòng màu</button>
                    <button class="btn btn-primary" onclick="generateResistorQuiz(quizState.bandCount)">🎲 Đổi màu ngẫu nhiên khác</button>
                </div>

                <!-- Hình vẽ điện trở ngẫu nhiên -->
                <div id="quiz-resistor-stage" class="diagram-box" style="max-width:620px;"></div>
                <div id="quiz-bands-summary" style="text-align:center; font-size:13.5px; margin:8px 0 14px 0; color:var(--amber-pale);"></div>

                <!-- Ô nhập câu trả lời -->
                <div class="quiz-answer-grid">
                    <div>
                        <label>Nhập trị số điện trở (*)</label>
                        <input type="text" id="quiz-Input-val" placeholder="VD: 27000 hoặc 27 hoặc 27.4" onkeydown="if(event.key==='Enter') checkResistorQuizAnswer()" />
                    </div>
                    <div>
                        <label>Đơn vị</label>
                        <select id="quiz-input-unit">
                            <option value="1">Ω (Ohm)</option>
                            <option value="1000">kΩ (Kilo Ohm)</option>
                            <option value="1000000">MΩ (Mega Ohm)</option>
                            <option value="1000000000">GΩ (Giga Ohm)</option>
                        </select>
                    </div>
                    <div>
                        <label>Sai số (Dung sai)</label>
                        <select id="quiz-input-tol">
                            <option value="0.5">± 0,5% (Xanh lục)</option>
                            <option value="1">± 1% (Nâu)</option>
                            <option value="2">± 2% (Đỏ)</option>
                            <option value="5" selected>± 5% (Kim nhũ)</option>
                            <option value="10">± 10% (Ngân nhũ)</option>
                            <option value="20">± 20% (Không màu - 3 vòng)</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" style="height:38px;" onclick="checkResistorQuizAnswer()">✅ Kiểm tra kết quả</button>
                </div>

                <div id="quiz-feedback-box"></div>
            </div>`;
        }

        function formatOhmReadable(ohm) {
            const clean = Number(ohm.toPrecision(10));
            if (clean >= 1e9) {
                return `${clean} Ω (hay ${(clean / 1e9).toString().replace('.', ',')} GΩ)`;
            }
            if (clean >= 1e6) {
                return `${clean} Ω (hay ${(clean / 1e6).toString().replace('.', ',')} MΩ)`;
            }
            if (clean >= 1e3) {
                return `${clean} Ω (hay ${(clean / 1e3).toString().replace('.', ',')} KΩ)`;
            }
            return `${clean.toString().replace('.', ',')} Ω`;
        }

        function generateResistorQuiz(bandCount) {
            quizState.bandCount = bandCount || 4;
            [3, 4, 5].forEach(n => {
                const btn = document.getElementById('btn-band-' + n);
                if (btn) {
                    if (n === quizState.bandCount) btn.classList.add('active-band');
                    else btn.classList.remove('active-band');
                }
            });

            const firstDigitPool = RESISTOR_COLORS.filter(c => c.digit !== null && c.digit >= 1);
            const otherDigitPool = RESISTOR_COLORS.filter(c => c.digit !== null);
            const multPool = RESISTOR_COLORS.filter(c => c.multExp !== null && c.multExp <= 6);
            const tolPool = RESISTOR_COLORS.filter(c => c.tol !== null);

            const pick = arr => arr[Math.floor(Math.random() * arr.length)];

            const b1 = pick(firstDigitPool);
            const b2 = pick(otherDigitPool);
            let bands = [];
            let sigValue = 0;
            let multBand = pick(multPool);
            let tolVal = 20;
            let tolBand = null;

            if (quizState.bandCount === 3) {
                bands = [b1, b2, multBand];
                sigValue = b1.digit * 10 + b2.digit;
                tolVal = 20;
            } else if (quizState.bandCount === 4) {
                tolBand = pick(tolPool);
                bands = [b1, b2, multBand, tolBand];
                sigValue = b1.digit * 10 + b2.digit;
                tolVal = tolBand.tol;
            } else {
                const b3 = pick(otherDigitPool);
                tolBand = pick(tolPool);
                bands = [b1, b2, b3, multBand, tolBand];
                sigValue = b1.digit * 100 + b2.digit * 10 + b3.digit;
                tolVal = tolBand.tol;
            }

            const exactOhm = Number((sigValue * Math.pow(10, multBand.multExp)).toPrecision(10));
            quizState.bands = bands;
            quizState.ohmValue = exactOhm;
            quizState.toleranceValue = tolVal;

            const tolSelect = document.getElementById('quiz-input-tol');
            if (tolSelect && quizState.bandCount === 3) {
                tolSelect.value = '20';
            }

            const stage = document.getElementById('quiz-resistor-stage');
            if (stage) {
                const xPositions = quizState.bandCount === 3
                    ? [215, 265, 315]
                    : (quizState.bandCount === 4 ? [205, 252, 299, 382] : [200, 240, 280, 320, 385]);

                let bandsSvg = '';
                bands.forEach((b, idx) => {
                    const x = xPositions[idx];
                    bandsSvg += `
                        <rect x="${x}" y="28" width="20" height="58" fill="${b.hex}" stroke="#0f172a" stroke-width="1.6"/>
                        <text x="${x + 10}" y="108" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Vòng ${idx + 1}</text>
                    `;
                });

                stage.innerHTML = `
                    <svg viewBox="0 0 600 125" width="100%" height="125" xmlns="http://www.w3.org/2000/svg">
                        <rect x="60" y="53" width="120" height="8" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>
                        <rect x="420" y="53" width="120" height="8" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>
                        <rect x="180" y="28" width="240" height="58" rx="6" fill="#93c5fd" stroke="#0f172a" stroke-width="2.2"/>
                        ${bandsSvg}
                    </svg>
                `;
            }

            const summaryEl = document.getElementById('quiz-bands-summary');
            if (summaryEl) {
                const desc = bands.map((b, i) => `<b>Vòng ${i + 1}:</b> ${b.name}`).join(' &nbsp;|&nbsp; ');
                const extra = quizState.bandCount === 3 ? ' &nbsp;|&nbsp; <b>Vòng sai số:</b> Không màu (±20%)' : '';
                summaryEl.innerHTML = `🎨 Các vòng màu hiện tại: ${desc}${extra}`;
            }

            const valInput = document.getElementById('quiz-Input-val');
            if (valInput) valInput.value = '';
            const fbBox = document.getElementById('quiz-feedback-box');
            if (fbBox) fbBox.innerHTML = '';
        }

        function parseUserResistanceInput(rawStr, unitMult) {
            if (!rawStr) return NaN;
            let s = rawStr.trim().toLowerCase().replace(/,/g, '.').replace(/ω|ohm|\s+/g, '');
            let factor = unitMult;
            if (s.endsWith('g')) {
                factor = 1e9;
                s = s.slice(0, -1);
            } else if (s.endsWith('m')) {
                factor = 1e6;
                s = s.slice(0, -1);
            } else if (s.endsWith('k')) {
                factor = 1e3;
                s = s.slice(0, -1);
            }
            const num = parseFloat(s);
            if (isNaN(num)) return NaN;
            return Number((num * factor).toPrecision(10));
        }

        function checkResistorQuizAnswer() {
            const rawVal = document.getElementById('quiz-Input-val').value;
            const unitMult = parseFloat(document.getElementById('quiz-input-unit').value || '1');
            const userTol = parseFloat(document.getElementById('quiz-input-tol').value || '5');
            const fbBox = document.getElementById('quiz-feedback-box');

            const userOhm = parseUserResistanceInput(rawVal, unitMult);
            if (isNaN(userOhm)) {
                fbBox.innerHTML = `<div class="quiz-feedback-err">⚠️ Vui lòng nhập giá trị số hợp lệ vào ô trả lời (ví dụ: <code>27000</code> hoặc <code>27</code> kèm đơn vị <code>kΩ</code>)!</div>`;
                return;
            }

            const expectedOhm = quizState.ohmValue;
            const expectedTol = quizState.toleranceValue;
            const isOhmCorrect = Math.abs(userOhm - expectedOhm) <= Math.max(1e-6, expectedOhm * 1e-4);
            const isTolCorrect = Math.abs(userTol - expectedTol) < 0.01;

            const b = quizState.bands;
            let formulaExplain = '';
            if (quizState.bandCount === 3) {
                formulaExplain = `
                    - <b>Vòng 1 (${b[0].name}):</b> Chữ số thứ nhất = <b>${b[0].digit}</b><br/>
                    - <b>Vòng 2 (${b[1].name}):</b> Chữ số thứ hai = <b>${b[1].digit}</b><br/>
                    - <b>Vòng 3 (${b[2].name}):</b> Hệ số nhân = <b>10<sup>${b[2].multExp}</sup></b><br/>
                    - <b>Sai số (3 vòng màu - Không màu):</b> Mặc định = <b>± 20%</b><br/>
                    👉 <b>Công thức:</b> (${b[0].digit}${b[1].digit}) × 10<sup>${b[2].multExp}</sup> = <b>${formatOhmReadable(expectedOhm)}</b>, sai số <b>± ${expectedTol}%</b>.
                `;
            } else if (quizState.bandCount === 4) {
                formulaExplain = `
                    - <b>Vòng 1 (${b[0].name}):</b> Chữ số hàng chục = <b>${b[0].digit}</b><br/>
                    - <b>Vòng 2 (${b[1].name}):</b> Chữ số hàng đơn vị = <b>${b[1].digit}</b><br/>
                    - <b>Vòng 3 (${b[2].name}):</b> Bội số cơ số 10 = <b>10<sup>${b[2].multExp}</sup></b><br/>
                    - <b>Vòng 4 (${b[3].name}):</b> Sai số = <b>± ${b[3].tol}%</b><br/>
                    👉 <b>Công thức:</b> (${b[0].digit}${b[1].digit}) × 10<sup>${b[2].multExp}</sup> = <b>${formatOhmReadable(expectedOhm)}</b>, sai số <b>± ${expectedTol}%</b>.
                `;
            } else {
                formulaExplain = `
                    - <b>Vòng 1 (${b[0].name}):</b> Chữ số thứ 1 = <b>${b[0].digit}</b><br/>
                    - <b>Vòng 2 (${b[1].name}):</b> Chữ số thứ 2 = <b>${b[1].digit}</b><br/>
                    - <b>Vòng 3 (${b[2].name}):</b> Chữ số thứ 3 = <b>${b[2].digit}</b><br/>
                    - <b>Vòng 4 (${b[3].name}):</b> Bội số cơ số 10 = <b>10<sup>${b[3].multExp}</sup></b><br/>
                    - <b>Vòng 5 (${b[4].name}):</b> Sai số = <b>± ${b[4].tol}%</b><br/>
                    👉 <b>Công thức:</b> (${b[0].digit}${b[1].digit}${b[2].digit}) × 10<sup>${b[3].multExp}</sup> = <b>${formatOhmReadable(expectedOhm)}</b>, sai số <b>± ${expectedTol}%</b>.
                `;
            }

            if (isOhmCorrect && isTolCorrect) {
                fbBox.innerHTML = `
                    <div class="quiz-feedback-ok">
                        <b>✅ CHÍNH XÁC! Xin chúc mừng!</b><br/>
                        Bạn đã đọc đúng trị số điện trở là <b>${formatOhmReadable(expectedOhm)}</b> với sai số <b>± ${expectedTol}%</b>.<br/>
                        <div class="divider"></div>
                        <b>📘 Giải thích chi tiết:</b><br/>
                        ${formulaExplain}
                    </div>
                `;
            } else {
                let reason = [];
                if (!isOhmCorrect) reason.push(`Trị số bạn nhập (${formatOhmReadable(userOhm)}) chưa khớp với đáp án (${formatOhmReadable(expectedOhm)})`);
                if (!isTolCorrect) reason.push(`Sai số bạn chọn (± ${userTol}%) chưa khớp với đáp án (± ${expectedTol}%)`);
                fbBox.innerHTML = `
                    <div class="quiz-feedback-err">
                        <b>❌ CHƯA CHÍNH XÁC!</b> (${reason.join(' & ')})<br/>
                        <b>🎯 Đáp án đúng:</b> <b>${formatOhmReadable(expectedOhm)}</b> — Sai số: <b>± ${expectedTol}%</b><br/>
                        <div class="divider"></div>
                        <b>📘 Giải thích cách đọc từng vòng màu:</b><br/>
                        ${formulaExplain}
                    </div>
                `;
            }
        }

        // ==========================================
        // MODULE CHUYÊN BIỆT 2: BẢNG MÀU ĐỌC TRỊ SỐ & BẢNG KÝ HIỆU SAI SỐ ĐIỆN CẢM (HÌNH 1.7)
        // ==========================================
        function buildInductorLearningSectionHtml() {
            return `
            <div class="divider"></div>
            <div class="glass-card" style="margin-top:18px;">
                <span class="tech-badge">🎨 PHẦN 1: BẢNG MÀU ĐỌC TRỊ SỐ ĐIỆN CẢM (CUỘN CẢM 4 VẠCH MÀU)</span>
                <h3 style="margin:8px 0 6px 0; font-family:var(--font-display); color:var(--amber-light);">📊 Bảng đọc màu cuộn cảm 4 vạch màu (Đơn vị chuẩn: μH)</h3>
                <p style="font-size:13.5px; color:var(--text-secondary); margin:0 0 10px 0; line-height:1.55;">
                    Trên thân cuộn cảm đúc thường có 4 vạch màu hoặc 5 vạch màu. Đối với <b>cuộn cảm 4 vạch màu</b>:
                    <b>Vòng 1 và Vòng 2</b> biểu thị các chữ số có nghĩa của giá trị điện cảm; <b>Vòng 3</b> biểu thị hệ số nhân (lũy thừa cơ số 10);
                    <b>Vòng 4</b> cho biết dung sai. Giá trị của điện cảm tính theo đơn vị <b>μH</b>.
                </p>
                <div style="overflow-x:auto;">
                    <table class="tech-table">
                        <thead>
                            <tr>
                                <th>Vòng / Biểu thị</th>
                                <th>Vòng 1<br/><span style="font-size:12px;font-weight:400;">Chữ số thứ 1</span></th>
                                <th>Vòng 2<br/><span style="font-size:12px;font-weight:400;">Chữ số thứ 2</span></th>
                                <th>Vòng 3<br/><span style="font-size:12px;font-weight:400;">Hệ số nhân (10<sup>x</sup>)</span></th>
                                <th>Vòng 4<br/><span style="font-size:12px;font-weight:400;">Dung sai</span></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="background:#fde047; color:#0f172a;"><td>Vàng kim</td><td>-</td><td>-</td><td>-10 (× 10<sup>-1</sup>)</td><td>+/- 5%</td></tr>
                            <tr style="background:#cbd5e1; color:#0f172a;"><td>Bạc</td><td>-</td><td>-</td><td>-100 (× 10<sup>-2</sup>)</td><td>+/- 10%</td></tr>
                            <tr style="background:#090d16; color:#ffffff;"><td>Đen</td><td>0</td><td>0</td><td>0 (× 10<sup>0</sup>)</td><td>+/- 20%</td></tr>
                            <tr style="background:#78350f; color:#ffffff;"><td>Nâu</td><td>1</td><td>1</td><td>1 (× 10<sup>1</sup>)</td><td>-</td></tr>
                            <tr style="background:#dc2626; color:#ffffff;"><td>Đỏ</td><td>2</td><td>2</td><td>2 (× 10<sup>2</sup>)</td><td>-</td></tr>
                            <tr style="background:#ea580c; color:#ffffff;"><td>Cam</td><td>3</td><td>3</td><td>3 (× 10<sup>3</sup>)</td><td>-</td></tr>
                            <tr style="background:#facc15; color:#0f172a;"><td>Vàng</td><td>4</td><td>4</td><td>4 (× 10<sup>4</sup>)</td><td>-</td></tr>
                            <tr style="background:#16a34a; color:#ffffff;"><td>Xanh lá</td><td>5</td><td>5</td><td>-</td><td>-</td></tr>
                            <tr style="background:#0284c7; color:#ffffff;"><td>Xanh dương</td><td>6</td><td>6</td><td>-</td><td>-</td></tr>
                            <tr style="background:#7e22ce; color:#ffffff;"><td>Tím</td><td>7</td><td>7</td><td>-</td><td>-</td></tr>
                            <tr style="background:#6b7280; color:#ffffff;"><td>Xám</td><td>8</td><td>8</td><td>-</td><td>-</td></tr>
                            <tr style="background:#f8fafc; color:#0f172a;"><td>Trắng</td><td>9</td><td>9</td><td>-</td><td>-</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="info-alert" style="margin-top:12px;">
                    <b>💡 Ví dụ đọc cuộn cảm 4 vạch màu:</b><br/>
                    Một cuộn cảm có mã màu với: <b>Vòng 1 màu Cam</b> (3), <b>Vòng 2 màu Xám</b> (8) ➔ số có nghĩa là <b>38</b>.<br/>
                    <b>Vòng 3 màu Nâu</b> tức hệ số nhân là 1 (nhân với <b>10<sup>1</sup></b>). <b>Vòng 4 màu Bạc</b> tức dung sai là <b>+/- 10%</b>.<br/>
                    👉 Như vậy, cuộn cảm có giá trị danh nghĩa là: <b>38 × 10<sup>1</sup> = 380 μH</b> và dung sai <b>10%</b>.
                </div>
            </div>

            <div class="glass-card" style="margin-top:18px;">
                <span class="tech-badge">🔢 PHẦN 2: HỆ THỐNG MÃ SỐ & BẢNG KÝ HIỆU SAI SỐ ĐIỆN CẢM</span>
                <h3 style="margin:8px 0 6px 0; font-family:var(--font-display); color:var(--amber-light);">📋 Bảng Ký hiệu Sai số (Dung sai) trên thân Cuộn cảm</h3>
                <p style="font-size:13.5px; color:var(--text-secondary); margin:0 0 10px 0; line-height:1.55;">
                    Trong hệ thống mã số (mã 3 hoặc 4 chữ số & chữ cái in trên thân cuộn cảm, tính theo đơn vị <b>μH</b>):<br/>
                    - <b>Hai chữ số đầu tiên:</b> Các chữ số có nghĩa của giá trị điện cảm.<br/>
                    - <b>Chữ số thứ ba:</b> Hệ số nhân (lũy thừa cơ số 10).<br/>
                    - <b>Chữ cái thứ tư:</b> Luôn là ký hiệu dung sai (sai số) tra theo bảng dưới đây:
                </p>
                <div style="overflow-x:auto;">
                    <table class="tech-table">
                        <thead>
                            <tr>
                                <th>Ký hiệu chữ cái</th>
                                <th>Dung sai (Sai số)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td><code>B</code></td><td>+/- 0.15 nH</td></tr>
                            <tr><td><code>C</code></td><td>+/- 0.2 nH</td></tr>
                            <tr><td><code>S</code></td><td>+/- 0.3 nH</td></tr>
                            <tr><td><code>D</code></td><td>+/- 0.5 nH</td></tr>
                            <tr><td><code>F</code></td><td>+/- 1%</td></tr>
                            <tr><td><code>G</code></td><td>+/- 2%</td></tr>
                            <tr><td><code>H</code></td><td>+/- 3%</td></tr>
                            <tr><td><code>J</code></td><td>+/- 5%</td></tr>
                            <tr><td><code>K</code></td><td>+/- 10%</td></tr>
                            <tr><td><code>L</code></td><td>+/- 15%</td></tr>
                            <tr><td><code>M</code></td><td>+/- 20%</td></tr>
                            <tr><td><code>V</code></td><td>+/- 25%</td></tr>
                            <tr><td><code>N</code></td><td>+/- 30%</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="info-alert" style="margin-top:12px;">
                    <b>💡 Ví dụ đọc mã số cuộn cảm (<code>102J</code>):</b><br/>
                    Nếu một cuộn cảm có mã số <b><code>102J</code></b> được in trên thân:<br/>
                    - Hai chữ số đầu tiên là <b>10</b> (số có nghĩa là 10);<br/>
                    - Chữ số thứ ba là <b>2</b> (nhân với <b>10<sup>2</sup></b>);<br/>
                    - Chữ cái <b>J</b> là dung sai bằng <b>+/- 5%</b> theo bảng trên.<br/>
                    👉 Như vậy độ tự cảm là: <b>10 × 10<sup>2</sup> = 1.000 μH</b> (hoặc <b>1 mH</b>) với dung sai <b>5%</b> (giá trị thực nằm trong khoảng từ <b>950 đến 1050 μH</b>).
                </div>
            </div>`;
        }

        // ==========================================
        // TRANG CHI TIẾT THIẾT BỊ & HÌNH ẢNH THỰC TẾ
        // ==========================================
        function navigateToDeviceDetail(modelId, deviceId, fallbackSymbol) {
            const model = modelsData.find(m => m.id === modelId);
            if (!model) return;
            let dev = (model.devices || []).find(d => d.device_id === deviceId);
            if (!dev && fallbackSymbol) {
                dev = (model.devices || []).find(d => d.symbol === fallbackSymbol);
            }
            if (!dev) return;

            selectedModelId = model.id;
            selectedDeviceId = dev.device_id;
            closeModal('modal-model');
            document.getElementById('view-main').style.display = 'none';
            document.getElementById('view-device-detail').style.display = 'block';
            renderDeviceDetailView();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function backToMainView() {
            selectedDeviceId = null;
            document.getElementById('view-device-detail').style.display = 'none';
            document.getElementById('view-main').style.display = 'block';
            renderMainWorkspace();
        }

        function renderDeviceDetailView() {
            const model = modelsData.find(m => m.id === selectedModelId);
            if (!model) return;
            const dev = (model.devices || []).find(d => d.device_id === selectedDeviceId);
            if (!dev) return;

            let specializedHtml = '';
            if (dev.device_id === 'h14-dientro' || model.diagram_type === 'fig_1_4') {
                specializedHtml = buildResistorLearningSectionHtml();
            } else if (dev.device_id === 'h17-cuonday' || model.diagram_type === 'fig_1_7') {
                specializedHtml = buildInductorLearningSectionHtml();
            }

            const realImages = dev.real_images || [];
            let galleryHtml = '';
            if (!realImages.length) {
                galleryHtml = `<div class="info-alert">🖼️ Chưa có hình ảnh thực tế nào cho thiết bị này. Hãy tải ảnh lên kèm chú thích ở khung bên cạnh để trực quan hóa bài học!</div>`;
            } else {
                galleryHtml = `<div class="real-images-cards-grid">`;
                realImages.forEach(img => {
                    galleryHtml += `
                    <div class="glass-card" style="padding:14px;">
                        <img src="${img.image_data}" style="width:100%; height:180px; object-fit:cover; border-radius:8px; background:var(--cream-sand);" />
                        <p style="font-size:13.5px; margin:10px 0; color:var(--text-secondary);"><b>📝 Chú thích:</b> ${escapeHtml(img.caption)}</p>
                        <button class="btn btn-secondary btn-full" onclick="deleteRealImage('${img.image_id}')">🗑️ Xóa ảnh</button>
                    </div>`;
                });
                galleryHtml += `</div>`;
            }

            document.getElementById('device-detail-content').innerHTML = `
                <div class="tech-hero-banner" style="text-align:left; padding:24px 28px;">
                    <span class="copper-device-badge" style="margin-bottom:8px;">⚡ CHI TIẾT PHẦN TỬ / THIẾT BỊ TRÊN MÔ HÌNH</span>
                    <h2 class="hero-title-glow" style="font-size:26px; margin:6px 0;">🔧 ${escapeHtml(dev.name)}</h2>
                    <span style="color:var(--text-secondary); font-size:14px;">
                        Thuộc mô hình: <b style="color:var(--amber-light);">${escapeHtml(model.title)}</b> (<code>${escapeHtml(model.symbol || '')}</code>)
                    </span>
                </div>

                <div class="detail-top-grid">
                    <div class="glass-card">
                        <div>
                            <h3 style="margin-top:0; font-family:var(--font-display); color:var(--amber-light);">📖 Khái niệm & Công thức</h3>
                            <p style="line-height:1.65; white-space:pre-line; color:var(--text-secondary);">${escapeHtml(dev.concept)}</p>
                            <div class="divider"></div>
                            <h3 style="font-family:var(--font-display); color:var(--amber-light);">⚙️ Ví dụ & Nội dung chi tiết</h3>
                            <p style="line-height:1.65; white-space:pre-line; color:var(--text-secondary);">${escapeHtml(dev.details)}</p>
                        </div>
                    </div>
                    <div class="glass-card">
                        <div>
                            <h3 style="margin-top:0; font-family:var(--font-display); color:var(--amber-light);">🏷️ Định danh Kỹ thuật</h3>
                            <div style="font-size:12.5px; color:var(--text-muted);">Ký hiệu trên sơ đồ</div>
                            <div style="font-size:26px; font-weight:700; font-family:var(--font-mono); color:var(--amber-cyber); margin:6px 0 16px 0;">
                                ${escapeHtml(dev.symbol || 'Không có ký hiệu')}
                            </div>
                            <p style="font-size:13.5px; color:var(--text-secondary);"><b>Mã định danh (ID):</b> <code>${escapeHtml(dev.device_id)}</code></p>
                            <p style="font-size:13.5px; color:var(--text-secondary);"><b>Danh mục:</b> ${escapeHtml(model.category)}</p>
                        </div>
                        <div>
                            <div class="divider"></div>
                            <button class="btn btn-primary btn-full" style="margin-top:10px;" onclick="openModelModal('${model.id}')">
                                🔍 Mở lại Sơ đồ Mô hình
                            </button>
                        </div>
                    </div>
                </div>

                ${specializedHtml}

                <div class="divider" style="margin-top:22px;"></div>
                <h3 style="margin:22px 0 14px 0; font-family:var(--font-display); color:var(--amber-light);">📸 Hình ảnh thực tế của thiết bị & Chú thích</h3>
                <div class="detail-gallery-grid">
                    <div>${galleryHtml}</div>
                    <div class="glass-card">
                        <div>
                            <h4 style="margin-top:0; font-family:var(--font-display); color:var(--amber-pale);">➕ Thêm hình ảnh thực tế mới</h4>
                            <div id="real-img-error" class="error-alert"></div>
                            <div style="margin-bottom:12px;">
                                <label>Tải ảnh thực tế từ thiết bị (.png, .jpg, .webp)</label>
                                <input type="file" id="real-img-file" accept="image/*" />
                            </div>
                            <div style="margin-bottom:12px;">
                                <label>Hoặc dán đường dẫn URL hình ảnh</label>
                                <input type="text" id="real-img-url" placeholder="https://example.com/device.jpg" />
                            </div>
                            <div style="margin-bottom:14px;">
                                <label>Chú thích hình ảnh thực tế (*)</label>
                                <textarea id="real-img-caption" rows="3" placeholder="VD: Hình thực tế linh kiện sử dụng trong phòng thí nghiệm..."></textarea>
                            </div>
                        </div>
                        <button class="btn btn-primary btn-full" onclick="addRealImage()">📸 Lưu hình ảnh & Chú thích</button>
                    </div>
                </div>
            `;

            if (dev.device_id === 'h14-dientro' || model.diagram_type === 'fig_1_4') {
                generateResistorQuiz(quizState.bandCount || 4);
            }
        }

        async function addRealImage() {
            const errBox = document.getElementById('real-img-error');
            errBox.style.display = 'none';
            const fileInput = document.getElementById('real-img-file');
            const urlInput = document.getElementById('real-img-url');
            const caption = document.getElementById('real-img-caption').value.trim();

            let imgData = '';
            if (fileInput.files && fileInput.files[0]) {
                imgData = await fileToBase64(fileInput.files[0]);
            } else if (urlInput.value.trim()) {
                imgData = urlInput.value.trim();
            }

            const res = await fetch(`/api/models/${selectedModelId}/devices/${selectedDeviceId}/images`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'add', image_data: imgData, caption: caption })
            });
            const data = await res.json();
            if (!data.ok) {
                errBox.textContent = data.error;
                errBox.style.display = 'block';
                return;
            }
            modelsData = data.models;
            showToast('📸 Đã thêm hình ảnh thực tế kèm chú thích thành công!');
            renderDeviceDetailView();
        }

        async function deleteRealImage(imageId) {
            const res = await fetch(`/api/models/${selectedModelId}/devices/${selectedDeviceId}/images`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'delete', image_id: imageId })
            });
            const data = await res.json();
            if (data.ok) {
                modelsData = data.models;
                showToast('🗑️ Đã xóa hình ảnh thực tế!');
                renderDeviceDetailView();
            }
        }

        // ==========================================
        // FORM THÊM / SỬA / XÓA MÔ HÌNH (CRUD - HỖ TRỢ KHÁI NIỆM NHIỀU DÒNG)
        // ==========================================
        function syncCrudDevicesDraftFromDom() {
            const items = document.querySelectorAll('#crud-devices-list .crud-device-item');
            if (!items.length) return;
            crudDevicesDraft = Array.from(items).map(el => ({
                device_id: el.getAttribute('data-dev-id') || '',
                symbol: (el.querySelector('.crud-dev-sym').value || '').trim(),
                name: (el.querySelector('.crud-dev-name').value || '').trim(),
                concept: el.querySelector('.crud-dev-concept').value || '',
                details: el.querySelector('.crud-dev-details').value || ''
            }));
        }

        function renderCrudDeviceRows() {
            const container = document.getById ? document.getById('crud-devices-list') : document.getElementById('crud-devices-list');
            if (!container) return;
            container.innerHTML = crudDevicesDraft.map((d, idx) => `
                <div class="crud-device-item" data-dev-id="${escapeHtml(d.device_id || '')}">
                    <div class="crud-device-item-header">
                        <span style="font-size:13px; font-weight:700; color:var(--amber-pale); font-family:var(--font-display);">
                            #${idx + 1} — Phần tử / Khái niệm
                        </span>
                        ${crudDevicesDraft.length > 1 ? `
                            <button type="button" class="btn btn-secondary" style="padding:4px 10px; font-size:12px; color:#fca5a5;" onclick="removeCrudDeviceRow(${idx})">
                                🗑️ Xóa mục này
                            </button>
                        ` : ''}
                    </div>
                    <div class="crud-device-grid-top">
                        <div>
                            <label>Ký hiệu (nhập <code>-</code> nếu không có)</label>
                            <input type="text" class="crud-dev-sym" value="${escapeHtml(d.symbol || '')}" placeholder="VD: Nguồn, R, i, hoặc -" />
                        </div>
                        <div>
                            <label>Tên thiết bị / khái niệm (*)</label>
                            <input type="text" class="crud-dev-name" value="${escapeHtml(d.name || '')}" placeholder="VD: Nguồn điện, Vòng (mạch vòng)..." />
                        </div>
                    </div>
                    <div class="crud-device-grid-bottom">
                        <div>
                            <label>Khái niệm (*) — Có thể nhấn Enter xuống dòng</label>
                            <textarea class="crud-dev-concept" rows="3" placeholder="Nhập khái niệm (hỗ trợ nhiều dòng)...">${escapeHtml(d.concept || '')}</textarea>
                        </div>
                        <div>
                            <label>Nội dung chi tiết / Công thức / Ví dụ (*) — Có thể xuống dòng</label>
                            <textarea class="crud-dev-details" rows="3" placeholder="Nhập nội dung chi tiết, công thức, ví dụ (hỗ trợ nhiều dòng)...">${escapeHtml(d.details || '')}</textarea>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function addCrudDeviceRow(dev) {
            syncCrudDevicesDraftFromDom();
            crudDevicesDraft.push(dev || {
                device_id: '',
                symbol: '',
                name: '',
                concept: '',
                details: ''
            });
            renderCrudDeviceRows();
        }

        function removeCrudDeviceRow(idx) {
            syncCrudDevicesDraftFromDom();
            if (crudDevicesDraft.length <= 1) return;
            crudDevicesDraft.splice(idx, 1);
            renderCrudDeviceRows();
        }

        function openCrudModal(modelId) {
            const errBox = document.getElementById('crud-error-box');
            errBox.style.display = 'none';
            document.getElementById('crud-diagram-file').value = '';
            if (window.innerWidth <= 900) toggleSidebar(false);

            if (modelId) {
                const m = modelsData.find(item => item.id === modelId);
                if (!m) return;
                document.getElementById('crud-id').value = m.id;
                document.getElementById('crud-title').value = m.title || '';
                document.getElementById('crud-symbol').value = m.symbol || '';
                document.getElementById('crud-category').value = m.category || '';
                document.getElementById('crud-status').value = m.status || 'completed';
                document.getElementById('crud-concept').value = m.concept || '';
                document.getElementById('crud-diagram-url').value =
                    (m.diagram_image && m.diagram_image.startsWith('http')) ? m.diagram_image : '';
                crudDevicesDraft = (m.devices || []).map(d => ({
                    device_id: d.device_id || '',
                    symbol: d.symbol ? d.symbol : '-',
                    name: d.name || '',
                    concept: d.concept || '',
                    details: d.details || ''
                }));
                if (!crudDevicesDraft.length) {
                    crudDevicesDraft = [{ device_id: '', symbol: '', name: '', concept: '', details: '' }];
                }
            } else {
                document.getElementById('crud-id').value = '';
                document.getElementById('crud-title').value = '';
                document.getElementById('crud-symbol').value = '';
                document.getElementById('crud-category').value = '1.1. Các khái niệm cơ bản trong mạch điện';
                document.getElementById('crud-status').value = 'completed';
                document.getElementById('crud-concept').value = '';
                document.getElementById('crud-diagram-url').value = '';
                crudDevicesDraft = [
                    {
                        device_id: '',
                        symbol: 'Nguồn',
                        name: 'Nguồn điện',
                        concept: 'Thiết bị tạo ra điện năng.\nBiến đổi các dạng năng lượng khác thành điện năng.',
                        details: '- Pin, ắc quy: Biến đổi hóa năng thành điện năng.\n- Máy phát điện: Biến đổi cơ năng thành điện năng.'
                    },
                    {
                        device_id: '',
                        symbol: '-',
                        name: 'Vòng (mạch vòng)',
                        concept: 'Đường dẫn khép kín qua các phần tử của mạch điện.',
                        details: 'Không có ký hiệu riêng trên sơ đồ.'
                    }
                ];
            }
            renderCrudDeviceRows();
            document.getElementById('modal-crud').classList.add('active');
        }

        async function submitCrudForm() {
            const errBox = document.getElementById('crud-error-box');
            errBox.style.display = 'none';

            syncCrudDevicesDraftFromDom();

            const fileInput = document.getElementById('crud-diagram-file');
            const urlVal = document.getElementById('crud-diagram-url').value.trim();
            let diagramImg = null;
            if (fileInput.files && fileInput.files[0]) {
                diagramImg = await fileToBase64(fileInput.files[0]);
            } else if (urlVal) {
                diagramImg = urlVal;
            }

            const payload = {
                id: document.getElementById('crud-id').value,
                title: document.getElementById('crud-title').value,
                symbol: document.getElementById('crud-symbol').value,
                category: document.getElementById('crud-category').value,
                status: document.getElementById('crud-status').value,
                concept: document.getElementById('crud-concept').value,
                devices: crudDevicesDraft,
                diagram_image: diagramImg
            };

            const res = await fetch('/api/models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!data.ok) {
                errBox.textContent = data.error;
                errBox.style.display = 'block';
                return;
            }
            modelsData = data.models;
            closeModal('modal-crud');
            showToast('✅ Đã lưu dữ liệu mô hình thành công!');
            renderMainWorkspace();
        }

        async function deleteModel(modelId) {
            if (!confirm('Bạn có chắc chắn muốn xóa mô hình này?')) return;
            const res = await fetch(`/api/models/${modelId}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.ok) {
                modelsData = data.models;
                showToast('🗑️ Đã xóa mô hình thành công!');
                renderMainWorkspace();
            }
        }

        async function handleImportJson(event) {
            const file = event.target.files[0];
            if (!file) return;
            try {
                const text = await file.text();
                const parsed = JSON.parse(text);
                const res = await fetch('/api/import', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ data: parsed })
                });
                const result = await res.json();
                if (!result.ok) {
                    alert(result.error);
                } else {
                    modelsData = result.models;
                    showToast(`📥 Đã nhập thành công ${modelsData.length} mô hình từ file JSON!`);
                    renderMainWorkspace();
                }
            } catch (e) {
                alert('Lỗi: File tải lên không phải là định dạng JSON hợp lệ!');
            }
            event.target.value = '';
        }

        async function saveGithubConfig() {
            const repo = document.getElementById('gh-repo').value.trim();
            const token = document.getElementById('gh-token').value.trim();
            const branch = document.getElementById('gh-branch').value.trim() || 'main';
            const res = await fetch('/api/github-sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'config', repo, token, branch })
            });
            const data = await res.json();
            if (!data.ok) {
                alert(data.error);
            } else {
                showToast('✅ Đã kết nối và đồng bộ lên GitHub thành công!');
                fetchModels();
            }
        }

        initResponsiveSidebarState();
        fetchModels();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


# Tự động khởi chạy máy chủ Flask & bật trình duyệt khi nhấn nút Run trong Visual Studio / VS Code
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    url = f"http://127.0.0.1:{port}"
    print(f"🚀 Đang khởi động Model ĐĐT Flask Server tại: {url}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=port, debug=False)