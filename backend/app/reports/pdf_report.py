import io
from datetime import datetime


class SimplePDFDocument:
    """
    Lightweight, zero-dependency PDF generator adhering to PDF-1.4 specification.
    Draws headers, styled tables, metadata blocks, and footers across pages.
    """

    def __init__(self, title: str, subtitle: str | None = None):
        self.title = title
        self.subtitle = subtitle
        self.pages: list[list[str]] = []
        self.current_page: list[str] = []
        self.width = 595.28   # A4 width in points
        self.height = 841.89  # A4 height in points
        self.margin = 40.0
        self.cursor_y = self.height - self.margin
        self._start_new_page(is_first=True)

    def _start_new_page(self, is_first: bool = False):
        if not is_first:
            self.pages.append(self.current_page)
            self.current_page = []

        self.cursor_y = self.height - self.margin
        self._draw_header()

    def _draw_header(self):
        y = self.cursor_y
        self.current_page.append("0.1 0.2 0.45 rg")  # Deep blue accent
        self.current_page.append(f"{self.margin} {y - 2} {self.width - 2 * self.margin} 2 re f")

        # Document Title
        self.current_page.append("BT")
        self.current_page.append("/F2 16 Tf")
        self.current_page.append("0.05 0.1 0.25 rg")
        self.current_page.append(f"1 0 0 1 {self.margin} {y - 22} Tm")
        self.current_page.append(f"({self._escape_text(self.title)}) Tj")
        self.current_page.append("ET")

        # Subtitle / Timestamp
        timestamp_str = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        sub_text = f"{self.subtitle}  |  {timestamp_str}" if self.subtitle else timestamp_str
        self.current_page.append("BT")
        self.current_page.append("/F1 9 Tf")
        self.current_page.append("0.4 0.45 0.5 rg")
        self.current_page.append(f"1 0 0 1 {self.margin} {y - 36} Tm")
        self.current_page.append(f"({self._escape_text(sub_text)}) Tj")
        self.current_page.append("ET")

        self.cursor_y = y - 55

    def add_section_header(self, text: str):
        if self.cursor_y < 120:
            self._start_new_page()

        y = self.cursor_y
        self.current_page.append("BT")
        self.current_page.append("/F2 12 Tf")
        self.current_page.append("0.1 0.2 0.35 rg")
        self.current_page.append(f"1 0 0 1 {self.margin} {y - 14} Tm")
        self.current_page.append(f"({self._escape_text(text)}) Tj")
        self.current_page.append("ET")

        self.current_page.append("0.85 0.88 0.92 rg")
        self.current_page.append(f"{self.margin} {y - 18} {self.width - 2 * self.margin} 1 re f")

        self.cursor_y = y - 28

    def add_table(self, headers: list[str], rows: list[list[str]], col_widths: list[float] | None = None):
        printable_width = self.width - 2 * self.margin
        num_cols = len(headers)

        if not col_widths:
            col_widths = [printable_width / num_cols] * num_cols
        else:
            total_w = sum(col_widths)
            col_widths = [(w / total_w) * printable_width for w in col_widths]

        row_height = 20.0

        if self.cursor_y < row_height * 3:
            self._start_new_page()

        self._draw_table_header(headers, col_widths, row_height)

        for idx, row in enumerate(rows):
            if self.cursor_y < row_height * 2:
                self._start_new_page()
                self._draw_table_header(headers, col_widths, row_height)

            y = self.cursor_y
            if idx % 2 == 1:
                self.current_page.append("0.96 0.97 0.99 rg")
                self.current_page.append(f"{self.margin} {y - row_height} {printable_width} {row_height} re f")

            self.current_page.append("0.9 0.92 0.94 rg")
            self.current_page.append(f"{self.margin} {y - row_height} {printable_width} 0.5 re f")

            curr_x = self.margin + 4
            for c_idx, cell_text in enumerate(row[:num_cols]):
                c_width = col_widths[c_idx]
                trimmed = self._truncate(str(cell_text), int(c_width / 6.5))
                self.current_page.append("BT")
                self.current_page.append("/F1 8.5 Tf")
                self.current_page.append("0.15 0.18 0.22 rg")
                self.current_page.append(f"1 0 0 1 {curr_x} {y - 14} Tm")
                self.current_page.append(f"({self._escape_text(trimmed)}) Tj")
                self.current_page.append("ET")
                curr_x += c_width

            self.cursor_y -= row_height

        self.cursor_y -= 15

    def _draw_table_header(self, headers: list[str], col_widths: list[float], row_height: float):
        y = self.cursor_y
        printable_width = self.width - 2 * self.margin

        self.current_page.append("0.2 0.3 0.5 rg")
        self.current_page.append(f"{self.margin} {y - row_height} {printable_width} {row_height} re f")

        curr_x = self.margin + 4
        for c_idx, h_text in enumerate(headers):
            c_width = col_widths[c_idx]
            trimmed = self._truncate(str(h_text), int(c_width / 7.0))
            self.current_page.append("BT")
            self.current_page.append("/F2 9 Tf")
            self.current_page.append("1.0 1.0 1.0 rg")
            self.current_page.append(f"1 0 0 1 {curr_x} {y - 14} Tm")
            self.current_page.append(f"({self._escape_text(trimmed)}) Tj")
            self.current_page.append("ET")
            curr_x += c_width

        self.cursor_y -= row_height

    def _draw_footer(self, page_num: int, total_pages: int, stream: list[str]):
        y = 25.0
        stream.append("0.8 0.85 0.9 rg")
        stream.append(f"{self.margin} {y + 12} {self.width - 2 * self.margin} 0.5 re f")

        stream.append("BT")
        stream.append("/F1 8 Tf")
        stream.append("0.5 0.55 0.6 rg")
        stream.append(f"1 0 0 1 {self.margin} {y} Tm")
        stream.append("(Network Monitoring and Visualization System (NMVS)) Tj")
        stream.append("ET")

        page_str = f"Page {page_num} of {total_pages}"
        stream.append("BT")
        stream.append("/F1 8 Tf")
        stream.append("0.5 0.55 0.6 rg")
        stream.append(f"1 0 0 1 {self.width - self.margin - 55} {y} Tm")
        stream.append(f"({page_str}) Tj")
        stream.append("ET")

    def build(self) -> bytes:
        if self.current_page:
            self.pages.append(self.current_page)

        total_pages = len(self.pages)
        for i, page in enumerate(self.pages):
            self._draw_footer(i + 1, total_pages, page)

        buf = io.BytesIO()
        offsets = []

        def _write(s: str):
            buf.write(s.encode("latin-1"))

        _write("%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        offsets.append(buf.tell())
        _write("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

        page_refs = [f"{4 + i * 2} 0 R" for i in range(total_pages)]
        offsets.append(buf.tell())
        _write(f"2 0 obj\n<< /Type /Pages /Kids [{ ' '.join(page_refs) }] /Count {total_pages} >>\nendobj\n")

        offsets.append(buf.tell())
        _write("3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n")

        offsets.append(buf.tell())
        font_bold_obj_num = 4 + total_pages * 2
        _write(f"{font_bold_obj_num} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n")

        for i, page_cmds in enumerate(self.pages):
            page_obj_id = 4 + i * 2
            stream_obj_id = page_obj_id + 1

            offsets.append(buf.tell())
            _write(
                f"{page_obj_id} 0 obj\n"
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.width:.2f} {self.height:.2f}] "
                f"/Contents {stream_obj_id} 0 R "
                f"/Resources << /Font << /F1 3 0 R /F2 {font_bold_obj_num} 0 R >> >> >>\n"
                f"endobj\n"
            )

            content_str = "\n".join(page_cmds) + "\n"
            content_bytes = content_str.encode("latin-1", errors="replace")

            offsets.append(buf.tell())
            _write(
                f"{stream_obj_id} 0 obj\n"
                f"<< /Length {len(content_bytes)} >>\n"
                f"stream\n"
            )
            buf.write(content_bytes)
            _write("endstream\nendobj\n")

        xref_offset = buf.tell()
        total_objs = font_bold_obj_num + 1

        all_offsets = {
            1: offsets[0],
            2: offsets[1],
            3: offsets[2],
            font_bold_obj_num: offsets[3]
        }
        for i in range(total_pages):
            all_offsets[4 + i * 2] = offsets[4 + i * 2]
            all_offsets[5 + i * 2] = offsets[5 + i * 2]

        _write(f"xref\n0 {total_objs}\n")
        _write("0000000000 65535 f \n")
        for obj_id in range(1, total_objs):
            off = all_offsets.get(obj_id, 0)
            _write(f"{off:010d} 00000 n \n")

        _write(
            f"trailer\n"
            f"<< /Size {total_objs} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        )

        return buf.getvalue()

    @staticmethod
    def _escape_text(text: str) -> str:
        text = str(text or "")
        return (
            text.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .encode("latin-1", errors="replace")
            .decode("latin-1")
        )

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        s = str(text or "").strip()
        if len(s) > max_chars:
            return s[:max_chars - 2] + ".."
        return s


def generate_executive_summary_pdf(
    devices: list,
    alerts: list,
    bandwidth_records: list,
    health_score: float
) -> bytes:
    doc = SimplePDFDocument(
        title="NMVS - Executive Network Health Report",
        subtitle=f"Overall Network Health: {health_score:.1f}%"
    )

    # 1. Device Summary Section
    doc.add_section_header("Device Inventory & Roles")
    headers = ["ID", "Device Name", "IP Address", "Device Type"]
    col_widths = [45.0, 180.0, 140.0, 150.0]
    dev_rows = [[str(d.id), d.name, d.ip, d.device_type] for d in devices[:15]]
    doc.add_table(headers, dev_rows, col_widths)

    # 2. Recent Alerts Section
    doc.add_section_header("Recent Network Incidents & Alerts")
    al_headers = ["ID", "IP", "Type", "Severity", "Status", "Created At"]
    al_widths = [40.0, 110.0, 105.0, 70.0, 80.0, 110.0]
    al_rows = []
    for a in alerts[:10]:
        dt = a.created_at.strftime("%Y-%m-%d %H:%M") if getattr(a, "created_at", None) else "N/A"
        al_rows.append([str(a.id), a.device_ip, a.alert_type, a.severity.upper(), a.status.upper(), dt])
    doc.add_table(al_headers, al_rows, al_widths)

    # 3. Latest Bandwidth Section
    if bandwidth_records:
        doc.add_section_header("Latest Bandwidth Performance")
        bw_headers = ["ID", "Target", "Download (Mbps)", "Upload (Mbps)", "Ping (ms)"]
        bw_widths = [50.0, 165.0, 110.0, 110.0, 80.0]
        bw_rows = []
        for b in bandwidth_records[:5]:
            dl = f"{b.download_mbps:.1f}" if b.download_mbps else "N/A"
            ul = f"{b.upload_mbps:.1f}" if b.upload_mbps else "N/A"
            p = f"{b.ping_ms:.1f}" if b.ping_ms else "N/A"
            bw_rows.append([str(b.id), b.ip, dl, ul, p])
        doc.add_table(bw_headers, bw_rows, bw_widths)

    return doc.build()
