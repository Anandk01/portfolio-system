from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("demo_portfolio.pdf", pagesize=A4)
styles = getSampleStyleSheet()
elements = []

elements.append(Paragraph("Consolidated Account Statement (CAS)", styles["Title"]))
elements.append(Paragraph("NSDL e-Services | Period: 01-Jan-2025 to 31-Dec-2025", styles["Normal"]))
elements.append(Spacer(1, 20))
elements.append(Paragraph("Investor: Demo Investor | PAN: XXXXX0000X", styles["Normal"]))
elements.append(Spacer(1, 20))

data = [
    ["Script", "ISIN", "Quantity", "Invested Value"],
    ["RELIANCE INDUSTRIES LTD", "INE002A01018", "10", "28500.00"],
    ["INFOSYS LIMITED", "INE009A01021", "15", "31200.00"],
    ["HDFC BANK LIMITED", "INE040A01034", "20", "33800.00"],
    ["TATA CONSULTANCY SERVICES", "INE467B01029", "8", "30400.00"],
    ["NIFTYBEES", "INF204KB14I2", "50", "24512.00"],
    ["GOLDBEES", "INF204KB17I5", "30", "10570.00"],
    ["NIPPON INDIA LIQUID FUND DIRECT GROWTH", "INF0R8F01091", "100", "9507.00"],
    ["AXIS BLUECHIP FUND DIRECT PLAN GROWTH", "INF846K01EW2", "200", "15000.00"],
    ["VODAFONE IDEA LIMITED", "INE669E01016", "500", "1076.00"],
    ["WIPRO LIMITED", "INE075A01022", "25", "14250.00"],
]

table = Table(data, colWidths=[200, 120, 70, 100])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 10),
    ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTSIZE", (0, 1), (-1, -1), 9),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
]))

elements.append(table)
elements.append(Spacer(1, 20))
elements.append(Paragraph("Total Portfolio Value: Rs. 1,98,815.00", styles["Normal"]))

doc.build(elements)
print("demo_portfolio.pdf created successfully!")
