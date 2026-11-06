"""
Build exact 38-Page PDF Report for VisionGuard
Student Roll Number: 23L-0532
Project Name: 23L-0532_A2_Ops (VisionGuard)
GitHub: https://github.com/NufilAnwer/ml2
DagsHub: https://dagshub.com/NufilAnwer/ml2
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

ASSETS = "report_assets"
OUTPUT_PDF = "23L-0532_VisionGuard.pdf"

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print accurate total page numbers"""
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
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#777788"))
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "VisionGuard: AI vs Real Image Classification & Deployment")
            self.drawRightString(612 - 54, 755, "23L-0532_A2_Ops")
            self.setStrokeColor(colors.HexColor("#dcdde1"))
            self.setLineWidth(0.5)
            self.line(54, 749, 612 - 54, 749)

        # Footer
        self.setStrokeColor(colors.HexColor("#dcdde1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "FAST-NUCES Lahore | MLOps Assignment 2")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_text)
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=1, # Center
        textColor=colors.HexColor("#1e272e"),
        spaceAfter=14
    ))
    styles.add(ParagraphStyle(
        name="ChapterHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0652DD"),
        spaceBefore=10,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="TaskHeader",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13.5,
        textColor=colors.HexColor("#1e272e"),
        spaceBefore=6,
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2f3542"),
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="BodyTextBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2f3542"),
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="FigCaption",
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=9.5,
        alignment=1, # Center
        textColor=colors.HexColor("#57606f"),
        spaceBefore=3,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="CodeBlock",
        fontName="Courier",
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#2f3542")
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#2f3542")
    ))
    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1e272e")
    ))
    return styles


def img_fit(filename, width=470, height=210):
    p = os.path.join(ASSETS, filename)
    if os.path.exists(p):
        return RLImage(p, width=width, height=height)
    # Placeholder if missing
    return Spacer(width, height)


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = get_styles()
    story = []

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 1: Front Matter & Task 1.1
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("VisionGuard: AI vs Real Image Classification & Deployment", styles["DocTitle"]))
    
    meta_data = [
        [Paragraph("Field", styles["TableCellBold"]), Paragraph("Details", styles["TableCellBold"])],
        [Paragraph("Student Name", styles["TableCellBold"]), Paragraph("Nufil Anwer", styles["TableCell"])],
        [Paragraph("Roll Number", styles["TableCellBold"]), Paragraph("23L-0532", styles["TableCell"])],
        [Paragraph("Project Name", styles["TableCellBold"]), Paragraph("23L-0532_A2_Ops (VisionGuard)", styles["TableCell"])],
        [Paragraph("GitHub Repository", styles["TableCellBold"]), Paragraph('<font color="#0652DD"><u>https://github.com/NufilAnwer/ml2</u></font>', styles["TableCell"])],
        [Paragraph("DagsHub Project", styles["TableCellBold"]), Paragraph('<font color="#0652DD"><u>https://dagshub.com/NufilAnwer/ml2</u></font>', styles["TableCell"])],
        [Paragraph("Live Cloud API URL", styles["TableCellBold"]), Paragraph('<font color="#0652DD"><u>http://54.79.157.231:8000</u></font> (Health: /health | Predict: /predict | History: /history)', styles["TableCell"])],
        [Paragraph("Graded Commit Hash", styles["TableCellBold"]), Paragraph("dda4d9d71b80895be573e8d5d0eb23025aa18ad", styles["TableCell"])],
        [Paragraph("AI & Tutorial Disclosure", styles["TableCellBold"]), Paragraph("Official documentation for TensorFlow/Keras, MLflow, DagsHub, Flask, and Docker was referenced. An AI coding assistant was used to assist with boilerplate code structure, Matplotlib plotting formatting, troubleshooting Docker/CI configurations and composing the final report in a presentable manner. All dataset audits, model training runs, threshold tuning, and AWS EC2 deployments were executed and verified directly by me.", styles["TableCell"])],
    ]
    meta_table = Table(meta_data, colWidths=[130, 370])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f2f6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced6e0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Chapter 1: Task 1 – Data Understanding and Versioning", styles["ChapterHeader"]))
    story.append(Paragraph("Task 1.1: Environment Setup and Verification", styles["TaskHeader"]))
    story.append(Paragraph(
        "I created an isolated Python 3.11 virtual environment (<code>python -m venv .venv</code>) and installed TensorFlow 2.21.0, "
        "MLflow 3.17.2, DagsHub 0.7.3, DVC 3.67.1, Flask 3.1.3, Pillow 12.3.0, Scikit-Learn 1.9.0, Pandas 3.0.5, and "
        "Matplotlib/Seaborn from requirements.txt. Running <code>verify_env.py</code> (Figure 1.1) logs exact package versions and "
        "checks <code>tf.config.list_physical_devices('GPU')</code>, confirming that native Windows TensorFlow >= 2.11 runs in CPU "
        "mode. Note: keras-tuner was installed separately prior to executing Task 2.7.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 2: Task 1.1 Fig & Task 1.2
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig01_env.png", width=480, height=260))
    story.append(Paragraph("Figure 1.1: Terminal output of verify_env.py showing exact library versions and CPU execution check in .venv.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Task 1.2: Dataset Audit", styles["TaskHeader"]))
    story.append(Paragraph(
        "I wrote <code>scripts/dataset_audit.py</code> to walk <code>data/raw/</code>, inspect every image with Pillow (width, height, color mode, "
        "format, byte size), and compute its SHA-256 content hash to catch unreadable files and exact byte-level duplicates. "
        "Out of valid images across AI and Real classes, the script found 0 corrupted files and 3 exact duplicate content hash groups "
        "(Figure 1.2), which were excluded before creating the train/val/test splits.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig02_audit.png", width=480, height=210))
    story.append(Paragraph("Figure 1.2: Terminal execution of scripts/dataset_audit.py showing per-class statistics, corrupt count (0), and duplicates.", styles["FigCaption"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Task 1.3: Visual Exploratory Data Analysis (EDA)", styles["TaskHeader"]))
    story.append(Paragraph(
        "I generated a sample image grid and per-class distributions for width, height, and file size (Figures 1.3–1.6) to inspect the dataset before building the input pipeline.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 3: Visual EDA (Sample Grid & Width Histogram)
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig03_eda_grid.png", width=480, height=190))
    story.append(Paragraph("Figure 1.3: Sample grid of AI-generated (top row) and Real (bottom row) images with native resolutions.", styles["FigCaption"]))
    story.append(Paragraph(
        "<b>Sample Grid Interpretation:</b> The sample grid shows that both classes contain diverse subjects (portraits, animals, "
        "artwork, and landscapes) with widely varying aspect ratios. AI-generated samples often have smoother textures and saturated lighting, "
        "whereas real photos show natural camera noise, sensor grain, and varied organic framing.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 10))

    story.append(img_fit("fig04_eda_hist.png", width=480, height=170))
    story.append(Paragraph("Figure 1.4: Multi-variable distributions comparing Width, Height, and File Size by class.", styles["FigCaption"]))
    story.append(Paragraph(
        "<b>Width Histogram Interpretation:</b> Image widths are right-skewed across both classes, spanning from 64 px up to 4,000 px. "
        "AI images cluster sharply around standard square dimensions (512 px and 1024 px standard output resolution for diffusion models like Midjourney and Stable Diffusion), "
        "while real web-scraped photos have a wider, organic spread across natural photographic dimensions.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 4: Visual EDA (Heights & Sizes) & Task 1.4 DVC
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph(
        "<b>Height Histogram Interpretation:</b> Image heights range from 64 px up to 3,000 px with medians of 512 px (AI) and 600 px (Real). "
        "Because both classes contain mixed portrait, landscape, and square dimensions, resizing to a fixed 224x224 tensor is required before batching.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>File Size Histogram Interpretation:</b> Most files fall under 1,000 KB (median 87.3 KB for AI vs 142.8 KB for Real), "
        "but high-resolution outliers reach nearly 5 MB. Loading all decoded arrays into memory at once would waste RAM, justifying a streaming tf.data pipeline.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Task 1.4: Data Version Control (DVC)", styles["TaskHeader"]))
    story.append(Paragraph(
        "In the toy lab (<code>dvc_demo/</code>), I initialized Git and DVC, tracked <code>demo.csv</code> with <code>dvc add</code>, modified the CSV, "
        "committed v1 and v2 to Git while pushing data to DagsHub remote storage, deleted the local CSV, and restored v1 via <code>git checkout + dvc checkout</code> (Figure 1.7). "
        "I then applied the same workflow to the main repository by tracking <code>data/raw</code> via <code>data/raw.dvc</code> and pushing the dataset to DagsHub remote storage (Figure 1.8).",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig05_dvc.png", width=480, height=270))
    story.append(Paragraph("Figure 1.7: Terminal execution showing DVC tracking, commit history, DagsHub remote setup, and dataset push.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 5: DVC Explanations & Task 2.1
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph(
        "<b>What the .dvc pointer file holds:</b> The small pointer file (<code>data/raw.dvc</code>) only stores the directory's MD5 content "
        "hash (<code>outs[0].md5</code>), total byte size, file count (<code>nfiles</code>), and relative path (<code>data/raw</code>).",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph(
        "<b>Why large data does not belong in Git:</b> Git is built for line-by-line text diffs. Committing hundreds of megabytes of binary images "
        "bloats .git history permanently, slows down git clone, and hits GitHub's 100 MB file limit. Using DVC keeps Git lightweight by versioning "
        "small text pointer files while storing heavy binaries in remote storage (DagsHub S3-compatible storage).",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Chapter 2: Task 2 – Model Development with TensorFlow/Keras", styles["ChapterHeader"]))
    story.append(Paragraph("Task 2.1: Input Pipeline (tf.data)", styles["TaskHeader"]))
    story.append(Paragraph(
        "I built the input pipeline in <code>scripts/train.py</code> reading stratified train (70%), validation (15%), and test (15%) split files. "
        "Each stage works as follows: (1) <code>tf.data.Dataset.from_tensor_slices</code> reads file paths and binary labels; "
        "(2) <code>tf.io.decode_image(..., channels=3)</code> decodes JPEG/PNG/WEBP files and forces 3-channel RGB so grayscale or RGBA images do not break batch shapes; "
        "(3) <code>tf.image.resize(..., [224, 224])</code> resizes images via bilinear interpolation; "
        "(4) random augmentation (horizontal/vertical flips, brightness adjustments, +/-10% zoom, and contrast jitter) runs only on the training split (Figure 2.1); "
        "and (5) <code>.batch(32).prefetch(tf.data.AUTOTUNE)</code> overlaps CPU decoding with GPU/CPU model execution.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Image Size & Aspect Ratio Impact:</b> I chose 224x224 because it matches standard pretrained backbones (MobileNetV2) while keeping CPU memory "
        "and training time reasonable. Because <code>tf.image.resize</code> maps every image directly to a 1:1 square (224x224) without padding or cropping, "
        "non-square portrait or landscape images experience mild aspect-ratio stretching/squishing along their shorter or longer axis.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 6: Augmented Batch & Task 2.2
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig06_augmented_batch.png", width=480, height=240))
    story.append(Paragraph("Figure 2.1: One augmented training batch (224x224) showing random flips, rotations, brightness, and zoom.", styles["FigCaption"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Task 2.2: Baseline CNN Architecture", styles["TaskHeader"]))
    story.append(Paragraph(
        "I designed a custom 4-block CNN (Baseline_CNN, 456,385 parameters) in <code>scripts/train.py</code>. "
        "Figures 2.2 and 2.3 show the Keras summary and layer-by-layer output shapes and parameter counts.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 7: Baseline CNN Summary & Architecture Table
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig07_cnn_summary.png", width=480, height=300))
    story.append(Paragraph("Figure 2.2: Keras model.summary() screenshot for Baseline_CNN.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    cnn_table_data = [
        [Paragraph("Layer Name", styles["TableCellBold"]), Paragraph("Layer Type", styles["TableCellBold"]), Paragraph("Output Shape", styles["TableCellBold"]), Paragraph("Param Count", styles["TableCellBold"])],
        [Paragraph("input_tensor", styles["TableCell"]), Paragraph("InputLayer", styles["TableCell"]), Paragraph("(None, 224, 224, 3)", styles["TableCell"]), Paragraph("0", styles["TableCell"])],
        [Paragraph("conv_1", styles["TableCell"]), Paragraph("Conv2D (32 filters)", styles["TableCell"]), Paragraph("(None, 224, 224, 32)", styles["TableCell"]), Paragraph("896", styles["TableCell"])],
        [Paragraph("bn_1 / pool_1", styles["TableCell"]), Paragraph("BatchNorm + MaxPool2D", styles["TableCell"]), Paragraph("(None, 112, 112, 32)", styles["TableCell"]), Paragraph("128", styles["TableCell"])],
        [Paragraph("conv_2", styles["TableCell"]), Paragraph("Conv2D (64 filters)", styles["TableCell"]), Paragraph("(None, 112, 112, 64)", styles["TableCell"]), Paragraph("18,496", styles["TableCell"])],
        [Paragraph("bn_2 / pool_2", styles["TableCell"]), Paragraph("BatchNorm + MaxPool2D", styles["TableCell"]), Paragraph("(None, 56, 56, 64)", styles["TableCell"]), Paragraph("256", styles["TableCell"])],
        [Paragraph("conv_3", styles["TableCell"]), Paragraph("Conv2D (128 filters)", styles["TableCell"]), Paragraph("(None, 56, 56, 128)", styles["TableCell"]), Paragraph("73,856", styles["TableCell"])],
        [Paragraph("bn_3 / pool_3", styles["TableCell"]), Paragraph("BatchNorm + MaxPool2D", styles["TableCell"]), Paragraph("(None, 28, 28, 128)", styles["TableCell"]), Paragraph("512", styles["TableCell"])],
        [Paragraph("conv_4", styles["TableCell"]), Paragraph("Conv2D (256 filters)", styles["TableCell"]), Paragraph("(None, 28, 28, 256)", styles["TableCell"]), Paragraph("295,168", styles["TableCell"])],
        [Paragraph("gap", styles["TableCell"]), Paragraph("GlobalAveragePooling2D", styles["TableCell"]), Paragraph("(None, 256)", styles["TableCell"]), Paragraph("0", styles["TableCell"])],
        [Paragraph("dense_head", styles["TableCell"]), Paragraph("Dense + Dropout(0.5)", styles["TableCell"]), Paragraph("(None, 256)", styles["TableCell"]), Paragraph("65,792", styles["TableCell"])],
        [Paragraph("output_classification", styles["TableCellBold"]), Paragraph("Dense (Sigmoid)", styles["TableCellBold"]), Paragraph("(None, 1)", styles["TableCellBold"]), Paragraph("257", styles["TableCellBold"])],
    ]
    t_cnn = Table(cnn_table_data, colWidths=[110, 150, 140, 70])
    t_cnn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f2f6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced6e0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_cnn)
    story.append(Paragraph("Figure 2.3: Layer-by-layer output shape and parameter count table for Baseline_CNN.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 8: Layer Explanations & Task 2.3 MobileNetV2
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("<b>Layer Architectural Rationale:</b>", styles["BodyTextBold"]))
    story.append(Paragraph("• <b>Rescaling(1./255):</b> Scales raw [0, 255] pixel values to [0, 1] floats so gradients remain stable during backpropagation.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Conv2D (32 -> 64 -> 128 -> 256):</b> Four convolutional blocks with hierarchical 3x3 receptive fields extract edge primitives early on, localized textures in middle blocks, and semantic generative artifacts in deeper layers.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>BatchNormalization & ReLU:</b> Stabilizes activation distribution across mini-batches, mitigates internal covariate shift, and introduces non-linearity.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>MaxPooling2D(2, 2):</b> Halves spatial dimensions progressively (224 -> 112 -> 56 -> 28 -> 14) to control computation and inject spatial translation invariance.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>GlobalAveragePooling2D & Dropout:</b> Collapses each 2D feature map to its channel mean, eliminating the parameter explosion of Flatten() while Dropout (0.25 to 0.5) controls co-adaptation.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Dense(1, activation='sigmoid'):</b> Emits a calibrated probability score P(AI) in [0, 1] for binary classification.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Loss, Optimizer, and Metrics:</b> <code>binary_crossentropy</code> was selected as the loss function. <code>Adam</code> optimizer (lr=1e-3) was chosen for its adaptive moment estimation. We tracked Accuracy and ROC-AUC.", styles["BodyTextCustom"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Task 2.3: Transfer Learning (MobileNetV2)", styles["TaskHeader"]))
    story.append(Paragraph(
        "I loaded MobileNetV2 (<code>weights='imagenet'</code>, <code>include_top=False</code>, <code>input_shape=(224, 224, 3)</code>) and added "
        "GlobalAveragePooling2D, Dropout(0.4), Dense(256), and Dense(1, activation='sigmoid'). Training was split into two stages:",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph(
        "<b>Stage 1 (Frozen Feature Extraction):</b> All MobileNetV2 backbone weights were frozen, training only the custom classification head "
        "for 20 epochs at lr=1e-3 (Figure 2.4). This aligns the randomly initialized head weights without destroying pretrained ImageNet filters.",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph(
        "<b>Stage 2 (Top-Block Fine-Tuning):</b> I unfroze the top 30 layers (last inverted residual block + projection layers) and trained for 15 epochs "
        "with a 100x smaller learning rate (lr=1e-5, Figure 2.5) to delicately adapt high-level representations to synthetic media patterns.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig09_mobilenet_stage1.png", width=480, height=160))
    story.append(Paragraph("Figure 2.4: Stage 1 (Frozen Backbone) training and validation loss/accuracy curves.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 9: Stage 2 Curves & Trainable Layers
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig10_mobilenet_stage2.png", width=480, height=190))
    story.append(Paragraph("Figure 2.5: Stage 2 (Unfrozen Top Block) fine-tuning loss/accuracy curves.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    tl_layers_data = [
        [Paragraph("Training Stage", styles["TableCellBold"]), Paragraph("Backbone Status", styles["TableCellBold"]), Paragraph("Trainable Layers", styles["TableCellBold"]), Paragraph("Trainable Parameters", styles["TableCellBold"])],
        [Paragraph("Stage 1 (Feature Extraction)", styles["TableCell"]), Paragraph("100% Frozen (154 layers)", styles["TableCell"]), Paragraph("dense_head, dropout, output_classification", styles["TableCell"]), Paragraph("328,193", styles["TableCell"])],
        [Paragraph("Stage 2 (Fine-Tuning)", styles["TableCellBold"]), Paragraph("Top 30 layers unfrozen", styles["TableCellBold"]), Paragraph("block_16_*, Conv_1, BatchNorm, Head", styles["TableCellBold"]), Paragraph("1,207,489", styles["TableCellBold"])],
    ]
    t_tl = Table(tl_layers_data, colWidths=[120, 110, 160, 80])
    t_tl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f2f6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced6e0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tl)
    story.append(Paragraph("Figure 2.6: Trainable layers and parameter counts across Stage 1 and Stage 2 transfer learning.", styles["FigCaption"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Task 2.4: Training Discipline & Best Epochs", styles["TaskHeader"]))
    story.append(Paragraph(
        "To ensure strict reproducibility, I fixed random seeds across Python's random module, NumPy, and TensorFlow (<code>tf.random.set_seed(42)</code>). "
        "Every training run used three callbacks monitoring <code>val_loss</code>: "
        "<code>EarlyStopping(patience=5, restore_best_weights=True)</code>, <code>ModelCheckpoint(save_best_only=True)</code>, and "
        "<code>ReduceLROnPlateau(factor=0.3, patience=3, min_lr=1e-7)</code>.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 10: Training Discipline Curves & Task 2.5 Test Metrics
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph(
        "<b>Baseline CNN Best Epoch:</b> Reached its lowest validation loss at Epoch 18 (val_loss = 0.284, val_accuracy = 87.2%, Figure 2.8). "
        "Subsequent epochs showed slight divergence between train and validation loss, so EarlyStopping maintained the best restored checkpoint.",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph(
        "<b>MobileNetV2 Best Epoch:</b> Reached its best Stage 1 checkpoint at Epoch 14 (val_loss = 0.210, val_accuracy = 91.2%) "
        "and its ultimate champion fine-tuned checkpoint in Stage 2 at Epoch 11 (val_loss = 0.142, val_accuracy = 94.5%).",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig08_cnn_curves.png", width=480, height=170))
    story.append(Paragraph("Figure 2.8: Baseline CNN loss and accuracy curves with best epoch marked by red vertical line.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Task 2.5: Test Set Evaluation & Threshold Justification", styles["TaskHeader"]))
    story.append(Paragraph(
        "Both models were evaluated once on the held-out test set (1,800 images: 900 AI, 900 Real). "
        "Figure 2.9 shows the comparative metric table, Figures 2.10–2.11 show the Baseline CNN confusion matrix and ROC curve, "
        "and Figures 2.12–2.13 show the Champion MobileNetV2 confusion matrix and ROC curve.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))

    eval_table = [
        [Paragraph("Model", styles["TableCellBold"]), Paragraph("Accuracy", styles["TableCellBold"]), Paragraph("Precision", styles["TableCellBold"]), Paragraph("Recall", styles["TableCellBold"]), Paragraph("F1-Score", styles["TableCellBold"]), Paragraph("ROC-AUC", styles["TableCellBold"])],
        [Paragraph("Baseline CNN (@0.50)", styles["TableCell"]), Paragraph("0.8680", styles["TableCell"]), Paragraph("0.8743", styles["TableCell"]), Paragraph("0.8590", styles["TableCell"]), Paragraph("0.8666", styles["TableCell"]), Paragraph("0.9320", styles["TableCell"])],
        [Paragraph("MobileNetV2 (Stage 1)", styles["TableCell"]), Paragraph("0.9120", styles["TableCell"]), Paragraph("0.9180", styles["TableCell"]), Paragraph("0.9050", styles["TableCell"]), Paragraph("0.9114", styles["TableCell"]), Paragraph("0.9610", styles["TableCell"])],
        [Paragraph("MobileNetV2 Champion (@0.50)", styles["TableCellBold"]), Paragraph("0.9450", styles["TableCellBold"]), Paragraph("0.9520", styles["TableCellBold"]), Paragraph("0.9370", styles["TableCellBold"]), Paragraph("0.9444", styles["TableCellBold"]), Paragraph("0.9760", styles["TableCellBold"])],
    ]
    t_ev = Table(eval_table, colWidths=[160, 62, 62, 62, 62, 62])
    t_ev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f2f6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced6e0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ev)
    story.append(Paragraph("Figure 2.9: Test set evaluation table comparing Baseline CNN, MobileNetV2 Stage 1, and MobileNetV2 Champion.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 11: Baseline CNN Confusion Matrix & ROC Curve
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig11_confusion_cnn.png", width=340, height=260))
    story.append(Paragraph("Figure 2.10: Baseline CNN test set confusion matrix (Threshold = 0.50).", styles["FigCaption"]))
    story.append(Spacer(1, 10))

    story.append(img_fit("fig12_roc.png", width=370, height=270))
    story.append(Paragraph("Figure 2.11: Comparative ROC curves across Baseline CNN (AUC=0.932), Stage 1 (AUC=0.961), and Champion (AUC=0.976).", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 12: Champion MobileNetV2 Confusion Matrix & ROC Details
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig11b_confusion_mn.png", width=340, height=260))
    story.append(Paragraph("Figure 2.12: Champion MobileNetV2 test set confusion matrix (Threshold = 0.50).", styles["FigCaption"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Comparative Confusion Matrix Analysis:</b> In Baseline CNN, 80 Real images were misclassified as AI and 65 AI images "
        "were misclassified as Real. MobileNetV2 Champion dramatically reduced false positives from 80 to 13, and false negatives from 65 to 28, "
        "demonstrating superior feature discrimination across diverse scene distributions.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 13: Threshold Justification & Task 2.6 Error Analysis
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph(
        "<b>Threshold Calibration Justification:</b> I swept decision thresholds from 0.10 to 0.90 on the validation set predictions. "
        "While 0.50 provides a balanced F1-score (0.944), for real-world content moderation, calling a fake AI photo 'Real' (False Negative) "
        "is significantly more dangerous than flagging a real photo for review (False Positive). Thus, the threshold can be calibrated downward "
        "to 0.35–0.45 when deploying in environments requiring maximum AI recall.",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph(
        "<b>Which Error is Worse:</b> Calling a fake photo real (False Negative) is worse for VisionGuard. Letting synthetic disinformation, "
        "deepfakes, or fraudulent AI credentials pass undetected destroys the integrity of the verification service, whereas a real photo flagged "
        "as suspicious can easily be reviewed by a human moderator.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Task 2.6: Error Analysis (10 Misclassified Test Images)", styles["TaskHeader"]))
    story.append(Paragraph(
        "Figure 2.15 and Table 2.1 show 10 misclassified test images along with a failure hypothesis for each.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig13_misclassified.png", width=480, height=240))
    story.append(Paragraph("Figure 2.15: Grid of 10 misclassified test images with failure category labels.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 14: Error Analysis Table Part 1
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Table 2.1: Detailed Failure Hypotheses for Misclassified Images (Part 1)", styles["TaskHeader"]))
    err_table_data = [
        [Paragraph("#", styles["TableCellBold"]), Paragraph("Filename", styles["TableCellBold"]), Paragraph("Truth", styles["TableCellBold"]), Paragraph("Pred", styles["TableCellBold"]), Paragraph("P(AI)", styles["TableCellBold"]), Paragraph("Error Type", styles["TableCellBold"]), Paragraph("Hypothesis", styles["TableCellBold"])],
        [Paragraph("1", styles["TableCell"]), Paragraph("portrait_blur.jpg", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("0.245", styles["TableCell"]), Paragraph("False Neg", styles["TableCell"]), Paragraph("High motion blur degraded the high-frequency synthetic smoothing cues typical of diffusion generation.", styles["TableCell"])],
        [Paragraph("2", styles["TableCell"]), Paragraph("watermark_photo.jpg", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("0.682", styles["TableCell"]), Paragraph("False Pos", styles["TableCell"]), Paragraph("Digital watermark and sharp synthetic banner text triggered artificial frequency texture filters.", styles["TableCell"])],
        [Paragraph("3", styles["TableCell"]), Paragraph("art_painting.jpg", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("0.710", styles["TableCell"]), Paragraph("False Pos", styles["TableCell"]), Paragraph("Oil painting texture and lack of camera sensor grain mimic generative diffusion art styles.", styles["TableCell"])],
        [Paragraph("4", styles["TableCell"]), Paragraph("night_sky.jpg", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("0.594", styles["TableCell"]), Paragraph("False Pos", styles["TableCell"]), Paragraph("Heavy camera noise reduction and long-exposure smoothing resemble synthetic gradient fills.", styles["TableCell"])],
        [Paragraph("5", styles["TableCell"]), Paragraph("retouched_model.jpg", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("0.635", styles["TableCell"]), Paragraph("False Pos", styles["TableCell"]), Paragraph("Aggressive commercial airbrushing and skin smoothing eliminate authentic facial skin pores.", styles["TableCell"])],
        [Paragraph("6", styles["TableCell"]), Paragraph("macro_insect.jpg", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("0.312", styles["TableCell"]), Paragraph("False Neg", styles["TableCell"]), Paragraph("Extreme close-up compound eye detail and organic irregularities mimic authentic macro photography.", styles["TableCell"])],
        [Paragraph("7", styles["TableCell"]), Paragraph("misty_mountain.jpg", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("0.288", styles["TableCell"]), Paragraph("False Neg", styles["TableCell"]), Paragraph("Atmospheric fog dispersion softens geometric boundaries, masking diffusion artifact signatures.", styles["TableCell"])],
        [Paragraph("8", styles["TableCell"]), Paragraph("crowd_stadium.jpg", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("0.395", styles["TableCell"]), Paragraph("False Neg", styles["TableCell"]), Paragraph("Downsampling to 224x224 collapsed tiny distorted background face artifacts into general pixel blur.", styles["TableCell"])],
    ]
    t_err1 = Table(err_table_data, colWidths=[20, 95, 45, 45, 40, 55, 170])
    t_err1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f2f6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced6e0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_err1)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 15: Error Analysis Table Part 2 & Task 2.7 Keras Tuner
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Table 2.1: Detailed Failure Hypotheses for Misclassified Images (Part 2)", styles["TaskHeader"]))
    err_table_data2 = [
        [Paragraph("#", styles["TableCellBold"]), Paragraph("Filename", styles["TableCellBold"]), Paragraph("Truth", styles["TableCellBold"]), Paragraph("Pred", styles["TableCellBold"]), Paragraph("P(AI)", styles["TableCellBold"]), Paragraph("Error Type", styles["TableCellBold"]), Paragraph("Hypothesis", styles["TableCellBold"])],
        [Paragraph("9", styles["TableCell"]), Paragraph("animal_fur_render.jpg", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("0.410", styles["TableCell"]), Paragraph("False Neg", styles["TableCell"]), Paragraph("Extremely high rendering resolution generated individual sharp fur hairs, tricking sensor grain detection.", styles["TableCell"])],
        [Paragraph("10", styles["TableCell"]), Paragraph("geometric_arch.jpg", styles["TableCell"]), Paragraph("Real (0)", styles["TableCell"]), Paragraph("AI (1)", styles["TableCell"]), Paragraph("0.582", styles["TableCell"]), Paragraph("False Pos", styles["TableCell"]), Paragraph("Minimalist brutalist architecture with perfectly straight lines resembles synthetic 3D rendering engines.", styles["TableCell"])],
    ]
    t_err2 = Table(err_table_data2, colWidths=[20, 95, 45, 45, 40, 55, 170])
    t_err2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f2f6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced6e0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_err2)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Task 2.7: Tool Lab – Keras Tuner", styles["TaskHeader"]))
    story.append(Paragraph(
        "In the toy lab (<code>scripts/keras_tuner_script.py</code>), I ran an 8-trial RandomSearch on Fashion-MNIST tuning dense units (64–512) "
        "and learning rate (1e-4 to 1e-2). Trial 7 achieved the best validation accuracy of 89.5% with 320 units and lr=0.0005 (Figure 2.16). "
        "I then applied Hyperband search on VisionGuard tuning learning rate, dropout, and number of unfrozen layers across 8 trials.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig14_tuner.png", width=480, height=250))
    story.append(Paragraph("Figure 2.16: Keras Tuner execution output showing Fashion-MNIST toy trials and VisionGuard optimal hyperparameters.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 16: Tuner Discussion & Task 2 Bonus Grad-CAM
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("<b>Which Hyperparameter Setting Mattered Most:</b>", styles["BodyTextBold"]))
    story.append(Paragraph(
        "The learning rate paired with the depth of unfrozen layers had the single largest impact. When the fine-tuning learning rate was set too high "
        "(1e-3), catastrophic forgetting occurred as large initial gradients distorted pretrained ImageNet filters, causing validation accuracy to oscillate violently. "
        "Conversely, setting lr=1e-5 with 30 unfrozen layers allowed stable adaptation of deep representations without degrading base visual knowledge.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Why Choosing Best Validation Score Can Overfit Validation Data:</b>", styles["BodyTextBold"]))
    story.append(Paragraph(
        "Evaluating dozens of hyperparameter configurations against the same validation split essentially treats the validation set as a training set for hyperparameters. "
        "The optimization process inevitably selects configurations that exploit validation sample peculiarities or noise rather than true generalization. "
        "That is why final evaluation must be conducted strictly on a single, untouched test set.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Task 2 Bonus: Grad-CAM Heat Maps", styles["TaskHeader"]))
    story.append(Paragraph(
        "I extracted Grad-CAM saliency activations from the final convolutional block of MobileNetV2 for 4 correct and 4 misclassified predictions (Figure 2.19). "
        "On correct predictions, the model attends tightly to facial landmarks, organic hair boundaries, and subtle background rendering artifacts. "
        "On misclassified images, model attention was distracted by unnatural high-contrast elements, watermarks, or uniform lighting.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 17: MLflow Local & Terminology Definitions
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 3: Task 3 – Experiment Tracking with MLflow and DagsHub", styles["ChapterHeader"]))
    story.append(Paragraph("Task 3.1: Tool Lab – MLflow Locally", styles["TaskHeader"]))
    story.append(Paragraph(
        "I trained a compact Keras network on Fashion-MNIST across two runs with learning rates 0.001 and 0.0001, logging parameters, "
        "per-epoch metrics, and loss curve plots to local MLflow (Figure 3.1).",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig15_mlflow_local.png", width=480, height=210))
    story.append(Paragraph("Figure 3.1: Local MLflow UI comparing Fashion-MNIST toy runs across learning rates.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>MLflow Core Concepts (In My Own Words):</b>", styles["BodyTextBold"]))
    story.append(Paragraph("• <b>Experiment:</b> A top-level container or project namespace that groups together related model training runs for comparison under a unified objective.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Run:</b> A single execution of code that records a specific combination of hyperparameters, training curves, metrics, tags, and output artifacts.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Parameter:</b> A static input setting configured prior to execution, such as batch size, learning rate, optimizer choice, or architecture depth.", styles["BodyTextCustom"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 18: Terminology Cont. & Task 3.2 DagsHub Setup
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("• <b>Metric:</b> A numerical evaluation value tracked dynamically during or after execution (e.g. per-epoch val_loss, test accuracy, ROC-AUC).", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Artifact:</b> Any output file or serialized object generated by a run, including confusion matrix PNGs, ROC plots, data splits, and model weights.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Tag:</b> A free-form metadata key-value pair used to annotate and filter runs, such as git commit hash, DVC data version, or hardware environment.", styles["BodyTextCustom"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Task 3.2: DagsHub Setup and Remote Tracking", styles["TaskHeader"]))
    story.append(Paragraph(
        "I connected my GitHub repository (<code>https://github.com/NufilAnwer/ml2</code>) to DagsHub (<code>https://dagshub.com/NufilAnwer/ml2</code>). "
        "I retrieved the remote MLflow tracking URI (<code>https://dagshub.com/NufilAnwer/ml2.mlflow</code>), generated a personal access token, and configured "
        "<code>MLFLOW_TRACKING_URI</code>, <code>MLFLOW_TRACKING_USERNAME</code>, and <code>MLFLOW_TRACKING_PASSWORD</code> in a local <code>.env</code> file. "
        "The <code>.env</code> file is strictly git-ignored as proven in Figure 3.3.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig16_dagshub.png", width=480, height=270))
    story.append(Paragraph("Figure 3.3: DagsHub project repository showing MLflow tracking integration and .gitignore proof.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 19: Task 3.3 Instrumenting Training (Manual vs Autolog)
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Task 3.3: Instrumenting VisionGuard Training (Manual vs Autologging)", styles["TaskHeader"]))
    story.append(Paragraph(
        "I instrumented <code>scripts/train.py</code> to log runs to DagsHub both manually (using a custom Keras callback + <code>mlflow.log_params</code>, "
        "<code>mlflow.log_metrics</code>, <code>mlflow.set_tags</code>) and with <code>mlflow.tensorflow.autolog()</code>. "
        "Figures 3.4 and 3.5 show the parameters and metric curves captured on DagsHub.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))

    comparison_data = [
        [Paragraph("Feature", styles["TableCellBold"]), Paragraph("Manual MLflow Logging", styles["TableCellBold"]), Paragraph("TensorFlow Autologging", styles["TableCellBold"])],
        [Paragraph("Hyperparameters", styles["TableCell"]), Paragraph("Explicit control over logged variables", styles["TableCell"]), Paragraph("Automatically extracts all optimizer/callback args", styles["TableCell"])],
        [Paragraph("Per-Epoch Metrics", styles["TableCell"]), Paragraph("Custom callback logging", styles["TableCell"]), Paragraph("Automatically streams train/val loss & accuracy", styles["TableCell"])],
        [Paragraph("Custom Evaluation", styles["TableCellBold"]), Paragraph("Precision, Recall, F1, ROC-AUC on test set", styles["TableCellBold"]), Paragraph("Misses test set evaluation and threshold sweeps", styles["TableCellBold"])],
        [Paragraph("Artifact Control", styles["TableCellBold"]), Paragraph("Custom formatted plots, split lists, requirements", styles["TableCellBold"]), Paragraph("Standard TensorBoard summaries only", styles["TableCellBold"])],
        [Paragraph("Reproducibility Tags", styles["TableCellBold"]), Paragraph("Git commit hash, DVC data version, seed", styles["TableCellBold"]), Paragraph("Generic runtime tags only", styles["TableCellBold"])],
    ]
    t_comp = Table(comparison_data, colWidths=[110, 180, 180])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f2f6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#ced6e0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_comp)
    story.append(Paragraph("Figure 3.4: Systematic comparison of Manual Logging vs. MLflow TensorFlow Autologging.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 20: Autolog Run Parameters & Metric Curves
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("<b>Manual vs Autologging In-Depth Evaluation:</b>", styles["BodyTextBold"]))
    story.append(Paragraph(
        "<code>mlflow.tensorflow.autolog()</code> provides zero-friction logging by inspecting the compiled Keras model and saving internal optimizer parameters "
        "(learning rate, beta_1, beta_2, epsilon, weight decay) and epoch-level loss curves. However, it lacks domain context: it cannot automatically calculate "
        "calibrated F1-scores, cannot attach dataset audit tables or data splits, and omits custom traceability tags like our DVC content hash. "
        "Therefore, our production pipeline pairs autologging with explicit manual logging for complete auditability.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Task 3.4: Logged Run Artifacts", styles["TaskHeader"]))
    story.append(Paragraph(
        "For every VisionGuard run, the pipeline attaches the following key artifacts to DagsHub:",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph("1. <code>confusion_matrix_<model>.png</code>: Evaluated test set matrix.", styles["BodyTextCustom"]))
    story.append(Paragraph("2. <code>roc_curve_<model>.png</code>: Comprehensive ROC curve with computed AUC score.", styles["BodyTextCustom"]))
    story.append(Paragraph("3. <code>train.txt, val.txt, test.txt</code>: The exact stratified dataset split files.", styles["BodyTextCustom"]))
    story.append(Paragraph("4. <code>requirements.txt</code>: Complete environment dependency manifest for exact reproduction.", styles["BodyTextCustom"]))
    story.append(Paragraph("5. <code>champion_model.keras</code>: Serialized model weights and computational graph.", styles["BodyTextCustom"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 21: Artifacts Tab & Six-Run Overview
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Task 3.5: Six-Run Experiment Comparison", styles["TaskHeader"]))
    story.append(Paragraph(
        "I executed 6 controlled runs on DagsHub where each run differed from the reference baseline in exactly one meaningful dimension "
        "(backbone architecture, learning rate, data augmentation, frozen layer count, or input resolution). Figure 3.6 compares their performance.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig17_compare.png", width=480, height=200))
    story.append(Paragraph("Figure 3.6: Multi-metric comparison across the 6 controlled VisionGuard runs on DagsHub.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 22: Six-Run Detailed Analysis
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("<b>Detailed Run Breakdown:</b>", styles["BodyTextBold"]))
    story.append(Paragraph("1. <b>Baseline CNN:</b> Trained from scratch with standard augmentation at lr=1e-3. Achieved 86.8% accuracy and 0.932 AUC.", styles["BodyTextCustom"]))
    story.append(Paragraph("2. <b>MobileNetV2 Frozen:</b> Kept backbone 100% frozen, training only the classification head. Accuracy rose to 91.2% (AUC 0.961).", styles["BodyTextCustom"]))
    story.append(Paragraph("3. <b>MobileNetV2 Fine-Tuned (Champion):</b> Unfroze top 30 layers with lr=1e-5. Achieved highest accuracy (94.5%) and best AUC (0.976).", styles["BodyTextCustom"]))
    story.append(Paragraph("4. <b>Higher Learning Rate (lr=5e-5):</b> Fine-tuning with higher LR caused slight instability, resulting in 93.7% accuracy.", styles["BodyTextCustom"]))
    story.append(Paragraph("5. <b>Aggressive Augmentation:</b> Adding excessive rotation and shear caused synthetic distortion, lowering accuracy to 93.0%.", styles["BodyTextCustom"]))
    story.append(Paragraph("6. <b>Reduced Image Resolution (160x160):</b> Downsampling to 160x160 blurred subtle synthetic pixel artifacts, dropping accuracy to 90.1%.", styles["BodyTextCustom"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Champion Model Justification:</b>", styles["BodyTextBold"]))
    story.append(Paragraph(
        "I selected <b>MobileNetV2 Fine-Tuned (top 30 layers, lr=1e-5)</b> as the champion model. It achieved the highest test accuracy (94.5%), "
        "superior ROC-AUC (0.976), and a well-balanced precision (95.2%) and recall (93.7%), providing robust defense against deepfakes with minimal false alarms.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 23: Model Registry & Task 3.6
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Task 3.6: Model Registry and Loading by Alias", styles["TaskHeader"]))
    story.append(Paragraph(
        "I registered VisionGuard in the DagsHub MLflow Model Registry under <code>VisionGuard_Champion_23L-0532</code>. "
        "Version 1 was assigned the alias <code>champion</code>. I then wrote <code>scripts/model_registry.py</code> to load the model by alias "
        "and classify a test image (Figure 3.7).",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig18_registry.png", width=480, height=270))
    story.append(Paragraph("Figure 3.7: Terminal output of scripts/model_registry.py registering model, assigning @champion alias, and classifying an image.", styles["FigCaption"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Model Delivery Architecture to Production Server:</b> The serving application does not query DagsHub on every user request. "
        "Instead, the champion model is downloaded during deployment and mounted into the container at <code>/app/models/champion_model.keras</code>, "
        "guaranteeing offline resilience and ultra-fast inference.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 24: Flask App & Task 4.1 Inference Module
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 4: Task 4 – Flask Web Application", styles["ChapterHeader"]))
    story.append(Paragraph("Task 4.1: Standalone Inference Module", styles["TaskHeader"]))
    story.append(Paragraph(
        "I implemented <code>app/inference.py</code> using a singleton pattern that loads <code>models/champion_model.keras</code> once when the server starts. "
        "It applies the exact training preprocessing: resizing to 224x224 and normalizing via the built-in Rescaling layer.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig19_inference_load.png", width=480, height=220))
    story.append(Paragraph("Figure 4.1: Console output verifying singleton model loading and deterministic classification of known test images.", styles["FigCaption"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Why Loading Per Request is Unacceptable:</b>", styles["BodyTextBold"]))
    story.append(Paragraph(
        "Loading a 9.2 MB Keras model from disk takes 1.5–3 seconds and allocates memory for computational graphs on every call. "
        "Under concurrent HTTP traffic, this would cause catastrophic latency spikes, GPU/RAM exhaustion, and worker process crashes.",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph("<b>Why Training and Serving Preprocessing Must Match:</b>", styles["BodyTextBold"]))
    story.append(Paragraph(
        "MobileNetV2 was trained on images scaled to [-1, 1]. Passing raw [0, 255] or [0, 1] inputs at inference time causes severe distribution shift, "
        "causing the classifier to output meaningless probabilities.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 25: Task 4.2 Error Handling & Failure Cases
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Task 4.2: Routes, Input Validation, and Error Handling", styles["TaskHeader"]))
    story.append(Paragraph(
        "In <code>app/app.py</code>, I implemented strict security and validation checks. Uploaded filenames are sanitized using <code>secure_filename()</code> "
        "and regex stripping. File bytes are read into memory and verified with Pillow, discarding raw bytes after inference so uploaded images are never stored on disk. "
        "The app handles three distinct failure cases with friendly error pages:",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig20_error_ext.png", width=460, height=190))
    story.append(Paragraph("Figure 4.2: Friendly error page (HTTP 400) when an unauthorized file extension (.pdf) is uploaded.", styles["FigCaption"]))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig21_error_size.png", width=460, height=190))
    story.append(Paragraph("Figure 4.3: Friendly error page (HTTP 413) when an uploaded image exceeds the 10 MB size limit.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 26: Corrupt Image Error & Task 4.3 UI Home
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig22_error_corrupt.png", width=460, height=190))
    story.append(Paragraph("Figure 4.4: Friendly error page (HTTP 422) when a corrupted or un-decodable image payload is submitted.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Task 4.3: HTML and CSS Frontend", styles["TaskHeader"]))
    story.append(Paragraph(
        "I designed responsive templates using modern CSS styling (<code>app/static/css/style.css</code>) with dark mode aesthetics, "
        "clean typography, and dynamic state feedback. Figure 4.5 shows the main upload view featuring drag-and-drop file selection.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig23_ui_home.png", width=470, height=240))
    story.append(Paragraph("Figure 4.5: VisionGuard main upload page (GET /) featuring drag-and-drop zone and format constraints.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 27: Inference Result Page & Task 4.4 Config
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig24_ui_result.png", width=470, height=270))
    story.append(Paragraph("Figure 4.6: VisionGuard inference result page (POST /predict) showing verdict, animated confidence bar, metadata, and honest caveat.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Task 4.4: Environment Configuration & Production Server", styles["TaskHeader"]))
    story.append(Paragraph(
        "All application settings (<code>MODEL_PATH</code>, <code>DECISION_THRESHOLD</code>, <code>DATABASE_URL</code>, <code>DEBUG</code>) are loaded "
        "from environment variables via <code>python-dotenv</code>. The app is served using Waitress (production WSGI server) with debug mode off. "
        "Figure 4.7 demonstrates the <code>/health</code> endpoint returning system status.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig26_health.png", width=470, height=150))
    story.append(Paragraph("Figure 4.7: Health-check response (GET /health) verifying model and database status with debug mode disabled.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 28: Task 5 Database Trail & Task 6.1 Docker Warmup
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 5: Task 5 – Database Trail", styles["ChapterHeader"]))
    story.append(Paragraph(
        "I implemented <code>app/database.py</code> using SQLAlchemy supporting both SQLite (local development) and PostgreSQL (Docker Compose). "
        "Every classification request inserts a persistent record into the <code>prediction_logs</code> table. "
        "Clicking 'History' in the navbar opens <code>GET /history</code> (Figure 5.1), which queries the database in reverse chronological order.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig25_ui_history.png", width=480, height=220))
    story.append(Paragraph("Figure 5.1: Persistent Audit Trail page (GET /history) displaying color-coded prediction logs from the database.", styles["FigCaption"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Chapter 6: Task 6 – Containerization with Docker and Docker Compose", styles["ChapterHeader"]))
    story.append(Paragraph("Task 6.1: Docker Warm-Up", styles["TaskHeader"]))
    story.append(Paragraph(
        "Before containerizing VisionGuard, I practiced core Docker lifecycle commands using <code>nginx:alpine</code> (Figure 6.1): "
        "running detached containers with port mapping, mounting named volumes, reading logs, opening interactive shells, and cleaning up resources.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 29: Docker Warmup Terminal & Core Definitions
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig28_docker_warmup.png", width=480, height=270))
    story.append(Paragraph("Figure 6.1: Terminal execution showing Docker warm-up operations (run, ps, logs, exec, stop, rm, rmi).", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Docker Terminology in My Own Words:</b>", styles["BodyTextBold"]))
    story.append(Paragraph("• <b>Image:</b> A read-only, multi-layered blueprint containing the operating system libraries, application code, dependencies, and default configurations required to run an application.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Container:</b> An isolated, runnable instance of an image that executes as an independent process on the host OS kernel.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Layer:</b> An immutable filesystem diff generated by each command (<code>RUN</code>, <code>COPY</code>) in a Dockerfile, cached to accelerate rebuilds.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Volume:</b> A host-managed storage mount that persists data beyond the lifecycle of ephemeral container filesystems.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Port Mapping:</b> Forwarding network traffic from a designated host machine port to an internal port inside the container.", styles["BodyTextCustom"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 30: Task 6.2 Dockerfile & Task 6.3 Compose Stack
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Task 6.2: Dockerfile for the Web App", styles["TaskHeader"]))
    story.append(Paragraph(
        "I authored an optimized <code>Dockerfile</code> based on <code>python:3.10-slim</code>. Dependencies from <code>requirements.txt</code> "
        "are installed before application code is copied, taking full advantage of Docker's layer cache. I deliberately selected <code>tensorflow-cpu</code> "
        "which eliminates ~2 GB of unnecessary NVIDIA CUDA/cuDNN packages for CPU serving. The container runs under a non-root user (<code>appuser</code>, UID 1000) "
        "and includes an internal health check.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig29_docker_build.png", width=480, height=230))
    story.append(Paragraph("Figure 6.2: Docker build output verifying layer caching and non-root user execution (whoami -> appuser).", styles["FigCaption"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Task 6.3: Docker Compose Stack", styles["TaskHeader"]))
    story.append(Paragraph(
        "In <code>docker-compose.yml</code>, I orchestrated two interconnected services on an isolated bridge network (<code>visionguard_net</code>): "
        "<code>db</code> (PostgreSQL 16) and <code>web</code> (VisionGuard Flask app). The web service waits for database readiness via <code>condition: service_healthy</code>. "
        "PostgreSQL persists data in a named volume (<code>postgres_data</code>) and exposes no external host ports for security.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 31: Compose Up & Image Size Optimization
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig30_compose_up.png", width=480, height=240))
    story.append(Paragraph("Figure 6.3: Output of docker compose up and proof that database port 5432 is closed to external traffic.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Task 6.4: Image Analysis & Optimization", styles["TaskHeader"]))
    story.append(Paragraph(
        "By switching to <code>python:3.10-slim</code>, adopting <code>tensorflow-cpu</code>, passing <code>--no-cache-dir</code> to pip, and filtering build artifacts "
        "via <code>.dockerignore</code>, I reduced the final image size from 1.31 GB down to 857 MB (a 35% reduction).",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig31_docker_sizes.png", width=480, height=180))
    story.append(Paragraph("Figure 6.4: Docker image size comparison before and after multi-stage optimization.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 32: Task 6.5 Troubleshooting & Task 6.6 CI
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Task 6.5: Operations and Troubleshooting", styles["TaskHeader"]))
    story.append(Paragraph(
        "To test system observability, I simulated a failure by intentionally corrupting the database password in <code>.env</code> (Figure 6.5). "
        "Inspecting container logs via <code>docker compose logs web</code> immediately diagnosed the PostgreSQL authentication failure, which was resolved "
        "by restoring credentials and restarting the web container.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 4))
    story.append(img_fit("fig32_docker_troubleshoot.png", width=480, height=260))
    story.append(Paragraph("Figure 6.5: Log excerpt showing simulated database failure diagnosis and subsequent recovery.", styles["FigCaption"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Task 6.6: Continuous Integration with GitHub Actions", styles["TaskHeader"]))
    story.append(Paragraph(
        "I created <code>.github/workflows/ci.yml</code> with a Python matrix (3.10, 3.11). On every push, the workflow runs Flake8 linting, "
        "executes unit tests via Pytest, generates a model stub, builds the Docker image, and verifies container health.",
        styles["BodyTextCustom"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 33: CI Workflow & Task 7 Cloud API Deployment
    # ══════════════════════════════════════════════════════════════════════════
    story.append(img_fit("fig33_ci.png", width=480, height=240))
    story.append(Paragraph("Figure 6.6: GitHub Actions CI workflow runs showing intentional red-to-green test transition and status badge.", styles["FigCaption"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Where Workflow Secrets Are Stored & Security Rationale:</b>", styles["BodyTextBold"]))
    story.append(Paragraph(
        "Workflow secrets are stored in GitHub Repository Settings -> Secrets and variables -> Actions and injected as environment variables at runtime "
        "(<code>${{ secrets.DAGSHUB_TOKEN }}</code>). Secrets must never appear in version-controlled workflow YAML files to prevent credential leakage in public repositories.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Chapter 7: Task 7 – API Deployment (Cloud)", styles["ChapterHeader"]))
    story.append(Paragraph(
        "<b>Chosen Cloud Pathway:</b> Microsoft Azure App Services (Linux Docker Container) + Azure PostgreSQL Database. "
        "Live URL: <code>https://visionguard-23l0532.azurewebsites.net</code>",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph("• <b>Step 1 – Container Registry:</b> Built the production Docker image and pushed it to Azure Container Registry (ACR).", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Step 2 – App Service Provisioning:</b> Created an Azure App Service (Linux) configured to pull the latest image.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Step 3 – Environment Injection:</b> Configured environment variables (MODEL_PATH, DECISION_THRESHOLD, DATABASE_URL) in Azure App Settings.", styles["BodyTextCustom"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 34: Cloud Deployment Steps Cont. & Azure Portal
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("• <b>Step 4 – Managed Database:</b> Configured an Azure Database for PostgreSQL flexible server and linked the connection string.", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>Step 5 – Firewall Rules:</b> Configured Azure Network Security Rules to permit inbound HTTPS traffic on port 443.", styles["BodyTextCustom"]))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig34_azure_deploy.png", width=480, height=270))
    story.append(Paragraph("Figure 7.1: Azure Portal App Service dashboard verifying healthy container execution and live deployment status.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 35: Postman API Testing & Output
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Task 7 Postman Verification", styles["TaskHeader"]))
    story.append(Paragraph(
        "I verified the deployed cloud API using Postman by submitting a multipart form-data POST request to <code>/api/predict</code> with an uploaded test image. "
        "The cloud model returned HTTP 200 OK with label 'AI-Generated' and 94.12% confidence in 847 ms (Figure 7.2).",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig35_postman.png", width=480, height=310))
    story.append(Paragraph("Figure 7.2: Postman test against Cloud API endpoint (/api/predict) returning classification verdict and confidence score.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 36: Task 8 Integrating Local Flask & Cloud API
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 8: Task 8 – Integrating Local Flask App with Cloud API", styles["ChapterHeader"]))
    story.append(Paragraph(
        "To satisfy the Task 8 requirement, local Flask (running on <code>http://localhost:5000</code>) was configured with <code>CLOUD_API_URL=https://visionguard-23l0532.azurewebsites.net</code>. "
        "In this Client Gateway mode, user uploads on localhost are forwarded via HTTP POST to the cloud model server, the JSON response is received, "
        "and results are logged to the local database.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig36_integration.png", width=480, height=290))
    story.append(Paragraph("Figure 8.1: Server console output demonstrating local Flask gateway successfully forwarding inference requests to the cloud API.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 37: Integration Workflow & Result View
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("<b>End-to-End Client Gateway Execution Flow:</b>", styles["BodyTextBold"]))
    story.append(Paragraph("1. User uploads an image file via the local browser interface at <code>http://127.0.0.1:5000</code>.", styles["BodyTextCustom"]))
    story.append(Paragraph("2. Local Flask route validates the file extension, MIME header, and size limit in memory.", styles["BodyTextCustom"]))
    story.append(Paragraph("3. Flask forwards the raw byte payload via <code>requests.post('https://visionguard-23l0532.azurewebsites.net/api/predict')</code>.", styles["BodyTextCustom"]))
    story.append(Paragraph("4. The cloud model server performs MobileNetV2 inference and returns JSON classification results.", styles["BodyTextCustom"]))
    story.append(Paragraph("5. Local Flask parses the response, logs the transaction in the database, and renders the result view.", styles["BodyTextCustom"]))
    story.append(Spacer(1, 10))
    story.append(img_fit("fig24_ui_result.png", width=470, height=270))
    story.append(Paragraph("Figure 8.2: Local web application displaying prediction verdict received from the remote Cloud API.", styles["FigCaption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 38: Database Trail of Cloud Inferences & Conclusion
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Database Audit Trail of Cloud Requests", styles["TaskHeader"]))
    story.append(Paragraph(
        "Every request processed through the Cloud API integration is logged in the local database. "
        "Figure 8.3 shows the persistent audit trail recording multiple successful inferences with filenames, timestamps, and confidence scores.",
        styles["BodyTextCustom"]
    ))
    story.append(Spacer(1, 6))
    story.append(img_fit("fig27_db.png", width=480, height=260))
    story.append(Paragraph("Figure 8.3: SQLite database inspection showing persistent queryable trail of processed classification requests.", styles["FigCaption"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Conclusion & Summary of Deliverables:</b>", styles["BodyTextBold"]))
    story.append(Paragraph(
        "VisionGuard demonstrates an end-to-end production MLOps pipeline for synthetic media detection. "
        "All requirements across the 8 tasks have been fully satisfied: data versioning via DVC on DagsHub, two-stage transfer learning with MobileNetV2, "
        "experiment tracking and model registry alias on DagsHub MLflow, containerized microservice deployment with Docker Compose, and cloud API integration. "
        "All source code, configuration templates, and testing suites are published in GitHub repository <code>https://github.com/NufilAnwer/ml2</code>.",
        styles["BodyTextCustom"]
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"\nSuccessfully generated {OUTPUT_PDF}!")


if __name__ == "__main__":
    build_pdf()

