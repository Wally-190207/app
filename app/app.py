import base64
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# Tự động khởi chạy Streamlit Server nếu người dùng nhấn nút Run (python app.py) trực tiếp trong VS Code
if __name__ == "__main__" and not st.runtime.exists():
    print("🚀 Đang khởi động Streamlit Web Server... Vui lòng mở link Local URL bên dưới:")
    sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)]))

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN CÔNG NGHỆ (TECH UI)
# ==========================================
st.set_page_config(
    page_title="Model ĐĐT - Kỹ thuật Điện - Điện tử",
    page_icon="⚡",
    layout="wide"
)

DATA_FILE = "data.json"


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
# 2. QUẢN LÝ DỮ LIỆU & LƯU TRỮ (DATA LAYER)
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


def load_data() -> list:
    """Đọc dữ liệu từ file data.json. Đảm bảo mỗi thiết bị đều có danh sách real_images."""
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
        # Đảm bảo tính tương thích cho trường real_images ở mọi thiết bị
        for model in data:
            for dev in model.get("devices", []):
                if "real_images" not in dev or not isinstance(dev["real_images"], list):
                    dev["real_images"] = []
        return data
    except (json.JSONDecodeError, IOError):
        return []


def save_data(data: list) -> None:
    """Ghi đè dữ liệu bền vững xuống file data.json."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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
    nhấn vào ký hiệu thiết bị (trên bản vẽ SVG hoặc nút ký hiệu).
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


# ==========================================
# 4. BẢN VẼ KỸ THUẬT SVG TƯƠNG TÁC (HÌNH 1.1 & HÌNH 1.2)
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


# ==========================================
# 5. DIALOGS (MODALS): TƯƠNG TÁC MÔ HÌNH & FORM CRUD
# ==========================================
@st.dialog("🔍 Sơ đồ Mô hình & Ký hiệu Thiết bị", width="large")
def open_model_modal(model: dict):
    """
    Modal hiển thị mô hình với bản vẽ kỹ thuật SVG và các 'Ký hiệu thiết bị' tương tác:
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

    st.subheader(f"📐 {model['title']} (`{model.get('symbol', 'N/A')}`)")
    st.caption(f"Phân loại: {model['category']} | Trạng thái: {model['status']}")
    st.markdown(f"**Khái niệm mô hình:** {model.get('concept', '')}")
    st.divider()

    st.markdown(
        "💡 *Hướng dẫn: **Di chuột** trực tiếp vào các ký hiệu trên bản vẽ kỹ thuật (Nguồn, Tải, Dây dẫn, Nhánh, Nút) "
        "để xem tên thiết bị. **Nhấn chuột trái** vào ký hiệu để chuyển sang trang nội dung chi tiết.*"
    )

    devices = model.get("devices", [])
    if not devices:
        st.info("Mô hình này chưa có thiết bị nào.")
        return

    symbol_devices = [d for d in devices if d.get("symbol", "").strip()]
    non_symbol_devices = [d for d in devices if not d.get("symbol", "").strip()]

    # 1. Hiển thị bản vẽ kỹ thuật SVG có nhúng điểm tương tác trực tiếp (Hotspots)
    if model.get("diagram_type") in ("fig_1_1", "fig_1_2"):
        render_interactive_svg_diagram(model)

    # 2. Hiển thị hàng nút Ký hiệu thiết bị có gắn on_click callback đảm bảo nhảy trang 100%
    if symbol_devices:
        with st.container(border=True):
            st.markdown("##### ⚡ Các Ký hiệu Thiết bị trên Mô hình (Nhấn trực tiếp trên bản vẽ hoặc nút ký hiệu bên dưới)")
            cols = st.columns(len(symbol_devices))
            for idx, dev in enumerate(symbol_devices):
                with cols[idx]:
                    if st.button(
                        f"🔣 {dev['symbol']}",
                        key=f"modal_sym_{model['id']}_{dev['device_id']}",
                        help=f"Tên thiết bị: {dev['name']} (Nhấn chuột trái để xem chi tiết)",
                        on_click=navigate_to_device_detail,
                        args=(model["id"], dev),
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
                        key=f"modal_nosym_{model['id']}_{dev['device_id']}",
                        help=f"Xem trang chi tiết: {dev['name']}",
                        on_click=navigate_to_device_detail,
                        args=(model["id"], dev),
                        use_container_width=True
                    ):
                        try:
                            st.rerun(scope="app")
                        except TypeError:
                            st.rerun()


@st.dialog("📝 Thêm / Chỉnh sửa Mô hình ĐĐT", width="large")
def open_crud_modal(edit_model: dict = None):
    """
    Dialog Form Thêm/Sửa Mô hình với kiểm tra dữ liệu (Validation) chặt chẽ bằng st.error.
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

            if is_edit:
                for item in st.session_state.models_data:
                    if item["id"] == edit_model["id"]:
                        item["title"] = title.strip()
                        item["symbol"] = symbol.strip()
                        item["category"] = category.strip()
                        item["status"] = status
                        item["concept"] = concept.strip()
                        item["devices"] = parsed_devices
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
                btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])
                with btn_col1:
                    if st.button(
                        "🔍 Mở Thẻ Mô hình",
                        key=f"open_card_{model['id']}",
                        type="primary",
                        use_container_width=True
                    ):
                        open_model_modal(model)
                with btn_col2:
                    if st.button("✏️ Sửa", key=f"edit_{model['id']}", use_container_width=True):
                        open_crud_modal(model)
                with btn_col3:
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
# 8. ĐIỀU HƯỚNG & BỐ CỤC CHÍNH (MAIN LAYOUT)
# ==========================================
def main():
    # Sidebar: Bộ lọc và Tìm kiếm theo [Tên, Khái niệm, Ký hiệu]
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
                        <b>di chuột</b> vào từng ký hiệu để xem tên thiết bị và <b>nhấn chuột trái</b> để mở trang chi tiết & hình ảnh thực tế.
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        render_models_workspace(search_name, search_concept, search_symbol, status_filter)


if __name__ == "__main__":
    main()