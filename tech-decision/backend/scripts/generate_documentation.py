import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime

# ----------------------------------------------------------------------
# TWO-PASS CANVAS FOR HEADER, FOOTER, AND TOTAL PAGE COUNT
# ----------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # 1. Cover Page styling (No header/footer)
        if self._pageNumber == 1:
            # Draw decorative side bar or background elements on cover page
            self.setFillColor(colors.HexColor("#0f172a")) # Dark background color
            self.rect(0, 0, 612, 792, fill=True, stroke=False)
            
            # Draw a nice accent bar
            self.setFillColor(colors.HexColor("#06b6d4")) # Cyan-500
            self.rect(0, 480, 612, 16, fill=True, stroke=False)
            self.restoreState()
            return

        # 2. Header (Pages 2+)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0891b2")) # Darker Cyan-600
        self.drawString(54, 752, "TECH DECISION — SYSTEM DOCUMENTATION")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b")) # Slate-500
        self.drawRightString(612 - 54, 752, "Architecture, API & Schema Deep-Dive")
        
        # Header line
        self.setStrokeColor(colors.HexColor("#cbd5e1")) # Slate-300
        self.setLineWidth(0.5)
        self.line(54, 744, 612 - 54, 744)

        # 3. Footer (Pages 2+)
        # Footer line
        self.setStrokeColor(colors.HexColor("#e2e8f0")) # Slate-200
        self.line(54, 52, 612 - 54, 52)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 38, "Confidential — Internal Developer Resource")
        self.drawRightString(612 - 54, 38, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


# ----------------------------------------------------------------------
# MAIN DOCUMENT GENERATION
# ----------------------------------------------------------------------
def generate_pdf(filename="Project_Documentation.pdf"):
    # Target letter size: 612 x 792 pt. Margins: 0.75" (54 pt)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom color palette (Slate & Cyan/Indigo)
    primary_color = colors.HexColor("#0f172a") # Slate-900 (Text)
    accent_color = colors.HexColor("#0891b2") # Cyan-600 (Headings)
    body_color = colors.HexColor("#334155") # Slate-700 (Body)
    light_bg = colors.HexColor("#f8fafc") # Slate-50 (Table/Box background)
    border_color = colors.HexColor("#cbd5e1") # Slate-300

    # Custom Typography Styles
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.white,
        spaceAfter=15
    )
    
    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#94a3b8"), # Slate-400
        spaceAfter=250
    )
    
    cover_metadata_style = ParagraphStyle(
        'CoverMetadata',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#cbd5e1") # Slate-300
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=accent_color,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=body_color,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=8
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=body_color
    )

    story = []

    # ==========================================
    # PAGE 1: COVER PAGE
    # ==========================================
    story.append(Spacer(1, 100))
    story.append(Paragraph("Tech Decision", cover_title_style))
    story.append(Paragraph("Full-Stack Deals Intelligence & Specification Analysis System", cover_subtitle_style))
    
    metadata_text = f"""
    <b>System Architecture & Developer Documentation</b><br/>
    <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
    <b>Version:</b> 1.0.0 (Release)<br/>
    <b>Workspace Path:</b> C:/Users/SAMSUNG/OneDrive/Desktop/My-Projects/33
    """
    story.append(Paragraph(metadata_text, cover_metadata_style))
    story.append(PageBreak())

    # ==========================================
    # PAGE 2: TABLE OF CONTENTS & OVERVIEW
    # ==========================================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(Spacer(1, 10))
    
    toc_data = [
        ["1. Executive Summary & Overview", "........................................................................................................", "Page 2"],
        ["2. Tech Stack & Workspace Structure", "........................................................................................................", "Page 3"],
        ["3. Database Schema & Migration Management", "........................................................................................................", "Page 4"],
        ["4. Backend Services Layer Deep-Dive", "........................................................................................................", "Page 5"],
        ["5. Frontend Layout & Interactive Components", "................................================........................................", "Page 6"],
        ["6. Local Execution & Environment Setup", "........................................................................................................", "Page 7"],
    ]
    
    t_toc = Table(toc_data, colWidths=[2.2*inch, 4.0*inch, 0.8*inch])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), body_color),
        ('TEXTCOLOR', (2,0), (2,-1), accent_color),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 30))

    story.append(Paragraph("1. Executive Summary & Overview", h1_style))
    story.append(Paragraph(
        "<b>Tech Decision</b> is a specialized web application designed to help consumers navigate the complex "
        "smartphone market. By tracking prices, crawling detailed specs, normalising raw configuration matrices, "
        "and validating commercial discounts, it provides users with honest, data-driven purchasing verdicts. "
        "The system aims to protect consumers from 'fake discounts'—a widespread practice where online retailers "
        "temporarily inflate listed prices (MRPs) just before sales to make discount percentages appear far higher "
        "than they actually are.",
        body_style
    ))
    story.append(Paragraph(
        "Key capabilities of the system include:",
        body_style
    ))
    story.append(Paragraph("• <b>Specs Normalization:</b> Automatically translates messy, inconsistent raw specifications fetched from mobile sites into clean data types (e.g. converting '5000 mAh' string to an integer).", bullet_style))
    story.append(Paragraph("• <b>Variant Extraction:</b> Recognises distinct product combinations based on RAM, storage capacity, and color, and maps pricing details directly to those variants.", bullet_style))
    story.append(Paragraph("• <b>Seller Trust Scoring:</b> Evaluates listing platforms (Amazon, Flipkart, Croma, Reliance) and independent merchants to guide buyers to reputable sources.", bullet_style))
    story.append(Paragraph("• <b>AI Verdict Generation:</b> Connects with LLMs to generate readable breakdowns, pros, cons, and buying recommendations.", bullet_style))
    story.append(PageBreak())

    # ==========================================
    # PAGE 3: TECH STACK & STRUCTURE
    # ==========================================
    story.append(Paragraph("2. Tech Stack & Workspace Structure", h1_style))
    story.append(Paragraph(
        "The project is structured as a full-stack, split-folder repository. "
        "The frontend is deployed to Vercel and handles browser routing and responsive layouts, while the backend API "
        "is a FastAPI service that performs the business logic, crawlers, calculations, and manages DB state.",
        body_style
    ))

    story.append(Paragraph("Technology Stack Matrix", h2_style))
    tech_matrix = [
        ["Layer", "Technology / Libraries Used", "Key Responsibilities"],
        ["Frontend", "Next.js 16 (App Router), TypeScript, Tailwind CSS, Lucide icons, shadcn/ui", "Search interface, variant selector, responsive charts, dynamic spec cards"],
        ["Backend", "FastAPI, Uvicorn, SQLAlchemy (ORM), Alembic, Pydantic, Dotenv, ReportLab", "REST API, data parsers, specs normalization engine, buying decision logic, PDF rendering"],
        ["Database", "PostgreSQL (Production) / SQLite (Local)", "Persistent tables for phones, specs, listings, AI insights, and variant prices"],
        ["AI Layer", "OpenAI API (GPT-4 / GPT-3.5)", "Summarizes battery, display, camera, and computes honest purchasing verdicts"]
    ]
    
    t_tech = Table(tech_matrix, colWidths=[1.1*inch, 2.7*inch, 3.2*inch])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), accent_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ]))
    for row_idx in range(len(tech_matrix)):
        for col_idx in range(len(tech_matrix[0])):
            cell_text = tech_matrix[row_idx][col_idx]
            style = table_header_style if row_idx == 0 else table_cell_style
            tech_matrix[row_idx][col_idx] = Paragraph(cell_text, style)
            
    story.append(t_tech)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Repository Workspace Layout", h2_style))
    dir_structure = """
c:/Users/SAMSUNG/OneDrive/Desktop/My-Projects/33/
├── README.md                          <- Root readme file
├── .gitignore                         <- Root git ignore settings
└── tech-decision/                     <- Project root folder
    ├── backend/                       <- FastAPI Application
    │   ├── main.py                    <- API entry point & CORS middleware
    │   ├── requirements.txt           <- Python dependencies list
    │   ├── alembic.ini                <- Alembic database migrations configuration
    │   ├── alembic/                   <- Migration script files
    │   └── app/
    │       ├── api/                   <- Routers (health.py, phones.py, discovery.py)
    │       ├── core/                  <- Config settings (.env loaders)
    │       ├── db/                    <- Session creators & Declarative Base
    │       ├── models/                <- SQLAlchemy db schemas
    │       ├── parsers/               <- GSMArena spec scraper & merchant scrapers
    │       ├── schemas/               <- Pydantic response models
    │       └── services/              <- Business logic & Engines (pricing, decision)
    └── frontend/                      <- Next.js 16 Web Application
        ├── package.json               <- Node dependencies list
        ├── next.config.mjs            <- Next.js specific compiler settings
        ├── tailwind.config.ts         <- Custom colors, layout & font tokens
        ├── components/                <- Shared UI parts (Search hero, UI inputs)
        └── app/                       <- Page routing layout
            ├── layout.tsx             <- Global wrapper & viewport configurations
            ├── page.tsx               <- Entry point / Search view
            └── phones/[slug]/         <- Dynamic detailed product page
    """
    story.append(Paragraph(dir_structure.replace(" ", "&nbsp;").replace("\n", "<br/>"), code_style))
    story.append(PageBreak())

    # ==========================================
    # PAGE 4: DATABASE SCHEMAS
    # ==========================================
    story.append(Paragraph("3. Database Schema & Migration Management", h1_style))
    story.append(Paragraph(
        "Persistence is designed around an ORM mapped layer using SQLAlchemy. "
        "The system supports full relational foreign key mappings with cascading deletes. "
        "Migrations are managed with Alembic, enabling smooth schema upgrades (e.g. moving from single-price "
        "listings to variant-specific pricing matrices).",
        body_style
    ))

    story.append(Paragraph("Entity-Relationship Overview", h2_style))
    story.append(Paragraph(
        "• <b>phones:</b> Core directory table storing model name, brand, slug, and launch pricing.<br/>"
        "• <b>phone_specs:</b> Holds normalized specs (ram_gb, storage_gb, chipset, charging_watts, display_size, refresh_rate_hz) and the raw crawled string fields.<br/>"
        "• <b>phone_insights:</b> Stores the AI summaries generated via OpenAI.<br/>"
        "• <b>phone_variants:</b> Contains mapped SKUs of RAM/Storage/Color combinations.<br/>"
        "• <b>variant_prices:</b> Mapped store-specific listings (Amazon, Flipkart) tracking MRPS and final prices for distinct variants.<br/>"
        "• <b>price_listings:</b> Mapped listings for base-model legacy mappings.",
        body_style
    ))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Database Table Columns Reference", h2_style))
    
    db_schema_table = [
        ["Table Name", "Column", "Data Type", "Constraints / Key"],
        ["phones", "id", "UUID", "PRIMARY KEY, Default UUIDv4"],
        ["", "slug", "String(210)", "UNIQUE, INDEX"],
        ["", "brand, model", "String", "INDEX"],
        ["phone_specs", "id", "UUID", "PRIMARY KEY"],
        ["", "phone_id", "UUID", "FOREIGN KEY (phones.id), UNIQUE"],
        ["", "battery_mah", "Integer", "Nullable"],
        ["", "refresh_rate_hz", "Integer", "Nullable"],
        ["", "display_size", "Float", "Nullable"],
        ["phone_variants", "id", "UUID", "PRIMARY KEY"],
        ["", "phone_id", "UUID", "FOREIGN KEY (phones.id)"],
        ["", "ram_gb, storage_gb", "Integer", "NotNull"],
        ["variant_prices", "id", "UUID", "PRIMARY KEY"],
        ["", "variant_id", "UUID", "FOREIGN KEY (phone_variants.id)"],
        ["", "platform", "String(100)", "NotNull (Amazon, Flipkart)"],
        ["", "listed_price, final_price", "Integer", "NotNull"],
        ["", "fake_discount_flag", "Boolean", "Default False"]
    ]
    
    t_db = Table(db_schema_table, colWidths=[1.4*inch, 1.4*inch, 1.4*inch, 2.8*inch])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), accent_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ]))
    for row_idx in range(len(db_schema_table)):
        for col_idx in range(len(db_schema_table[0])):
            cell_text = db_schema_table[row_idx][col_idx]
            style = table_header_style if row_idx == 0 else table_cell_style
            db_schema_table[row_idx][col_idx] = Paragraph(cell_text, style)
            
    story.append(t_db)
    story.append(PageBreak())

    # ==========================================
    # PAGE 5: BACKEND SERVICES LAYER
    # ==========================================
    story.append(Paragraph("4. Backend Services Layer Deep-Dive", h1_style))
    story.append(Paragraph(
        "The core intelligence of Tech Decision resides in its modular backend service engines. "
        "These services are isolated in the `app/services` directory, decoupling data models from business logic.",
        body_style
    ))

    story.append(Paragraph("Pricing Engine & Fake Discount Detection", h2_style))
    story.append(Paragraph(
        "The <b>PricingService</b> aggregates prices dynamically if listings are older than 1 hour. "
        "It leverages web parsers (`AmazonParser`, `FlipkartParser`, etc.) to extract raw listed price and MRP. "
        "The <b>FakeDiscountDetector</b> then analyzes the difference: "
        "if the platform-stated MRP is significantly higher than the launch price or previous averages, it flags "
        "a possible 'fake discount' and recalculates the <i>discount authenticity score</i>. "
        "It deducts coupon and bank cashbacks to compute the true <b>Best Effective Price</b>.",
        body_style
    ))

    story.append(Paragraph("Decision Engine Verdict Classifier", h2_style))
    story.append(Paragraph(
        "The <b>DecisionEngine</b> calculates a value score out of 100 based on hardware specs, "
        "adjusted by RAM/storage upgrades on variants. It then matches these against competitors' indexes and historic price fluctuations. "
        "The decision is categorized into one of four states:",
        body_style
    ))

    decision_states = [
        ["Verdict State", "Criteria", "Typical Recommendation Summary"],
        ["BUY_NOW", "Price is near historical low and specs offer great value.", "Excellent time to buy — price is at its absolute lowest."],
        ["WAIT_FOR_PRICE_DROP", "Current platform price is > 10% higher than historical lows.", "Wait — phone is currently marked up. Hold off for a sale."],
        ["BUY_COMPETITOR", "Another model has a value score > 3 points higher at similar pricing.", "Consider the competitor model instead for better hardware value."],
        ["SKIP", "Specs are weak (value score < 60) or price listings are missing.", "Skip this model due to poor specification-to-price ratio."]
    ]
    
    t_dec = Table(decision_states, colWidths=[1.8*inch, 2.2*inch, 3.0*inch])
    t_dec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), accent_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ]))
    for row_idx in range(len(decision_states)):
        for col_idx in range(len(decision_states[0])):
            cell_text = decision_states[row_idx][col_idx]
            style = table_header_style if row_idx == 0 else table_cell_style
            decision_states[row_idx][col_idx] = Paragraph(cell_text, style)
            
    story.append(t_dec)
    story.append(Spacer(1, 10))

    story.append(Paragraph("AI interpretation & Summary Services", h2_style))
    story.append(Paragraph(
        "To present raw specs in an understandable format, the <b>DeviceSummaryService</b> and "
        "<b>InsightGenerator</b> parse technical benchmarks into written summaries. "
        "They generate heavy-use vs normal-use battery expectations, highlight camera low-light "
        "performance, and provide a single-sentence honest verdict, caching them in the `phone_interpretations` "
        "and `phone_insights` tables to avoid duplicate API calls to OpenAI.",
        body_style
    ))
    story.append(PageBreak())

    # ==========================================
    # PAGE 6: FRONTEND LAYOUT & VIEWS
    # ==========================================
    story.append(Paragraph("5. Frontend Layout & Interactive Components", h1_style))
    story.append(Paragraph(
        "The user interface is built on Next.js 16 and is fully styled with tailwindcss to create a premium, "
        "futuristic dark mode theme. It leverages glassmorphic panel elements, custom gradients, and micro-interactions.",
        body_style
    ))

    story.append(Paragraph("Search Hero with Autocomplete & Keyboard Navigation", h2_style))
    story.append(Paragraph(
        "The entry page (`frontend/app/page.tsx`) renders the `SearchHero` component. "
        "As users type, it calls `GET /api/discovery/search` with debouncing (300ms) to load results. "
        "It supports complete keyboard accessibility (ArrowDown, ArrowUp, Enter, Escape) to navigate the results list "
        "and highlights 'Best Match' badges if match scores exceed 90%.",
        body_style
    ))

    story.append(Paragraph("Dynamic Variant Selector", h2_style))
    story.append(Paragraph(
        "Inside the product detail page, users can click variant chips for RAM, storage, or color. "
        "Choosing a different variant triggers dynamic price changes: "
        "it calls the backend prices endpoint with the `variant_id` query parameter, "
        "and recalculates the estimated launch price in real-time, adjusting discount gauges instantly.",
        body_style
    ))

    story.append(Paragraph("Price Comparison & Inflation Indicator Panel", h2_style))
    story.append(Paragraph(
        "The `PriceComparisonSection` displays a listing table comparing all active merchants. "
        "If a listing has a high discount flag (inflated MRP), an 'Inflation Alert' icon is rendered. "
        "It calculates trust scores using seller reviews to help buyers judge merchant reliability.",
        body_style
    ))

    story.append(Paragraph("Client-Side Fetch Fallback & Error Handling", h2_style))
    story.append(Paragraph(
        "To ensure robust client execution, page loading states are rendered using animated Pulse skeletons. "
        "Furthermore, server components include dynamic route safety: if a phone cannot be found in the database during "
        "metadata generation or initialization, the application captures the error, outputs diagnostics (such as the target slug), "
        "and presents a helpful debugging card indicating the root cause (e.g. missing API configuration or unseeded database).",
        body_style
    ))
    story.append(PageBreak())

    # ==========================================
    # PAGE 7: LOCAL SETUP GUIDE
    # ==========================================
    story.append(Paragraph("6. Local Execution & Environment Setup", h1_style))
    story.append(Paragraph(
        "Follow these steps to run the complete stack locally for development and testing.",
        body_style
    ))

    story.append(Paragraph("Step A — Backend Server Setup", h2_style))
    backend_setup_commands = """
# 1. Navigate to the backend directory
cd tech-decision/backend

# 2. Create the virtual environment
python -m venv .venv

# 3. Activate the environment
.venv\\Scripts\\activate

# 4. Install required dependencies
pip install -r requirements.txt

# 5. Set up environment variables (.env file)
# DATABASE_URL=sqlite:///./tech_decision.db
# FRONTEND_URL=http://localhost:3000
# OPENAI_API_KEY=your_key_here

# 6. Apply database schemas and migrations
alembic upgrade head

# 7. Seed sample phone data
python scripts/seed.py

# 8. Start uvicorn development server
python -m uvicorn main:app --host 127.0.0.1 --port 8000
"""
    story.append(Paragraph(backend_setup_commands.replace(" ", "&nbsp;").replace("\n", "<br/>"), code_style))

    story.append(Paragraph("Step B — Frontend Client Setup", h2_style))
    frontend_setup_commands = """
# 1. Navigate to the frontend directory
cd tech-decision/frontend

# 2. Install Node dependencies
npm install

# 3. Configure local environment variables (.env.local)
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# 4. Run next development server
npm run dev
"""
    story.append(Paragraph(frontend_setup_commands.replace(" ", "&nbsp;").replace("\n", "<br/>"), code_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Health Checks & API Verification", h2_style))
    story.append(Paragraph(
        "Verify the local services are running correctly by checking the health endpoint in your browser: "
        "<code style='color:#0891b2;'>http://localhost:8000/health</code>, which should return "
        "<code>{\"status\":\"ok\"}</code>. The swagger docs are interactive and accessible via "
        "<code style='color:#0891b2;'>http://localhost:8000/docs</code>.",
        body_style
    ))

    # Build the PDF using our custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    generate_pdf()
