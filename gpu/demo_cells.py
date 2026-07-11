"""
Critto — AMD GPU demo cells (for the demo-video "runs on AMD" shot).

Run these in the AMD AI Notebook's Python 3 (ipykernel) — the ROCm kernel.
Cell 1 loads the model (run once, before recording). Cell 2 is what you film.

The line "Running on: <AMD GPU> | ROCm 7.2" is the on-screen AMD proof.
"""

# ==================== CELL 1 — setup (run once, off-camera) ====================
import subprocess, sys, io, csv, urllib.request, torch
try:
    import open_clip
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "open_clip_torch"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "ftfy", "regex", "huggingface_hub", "pillow"])
    import open_clip
from PIL import Image
from IPython.display import display

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
GPU = "CPU"
if DEVICE == "cuda":
    _p = torch.cuda.get_device_properties(0)
    GPU = (torch.cuda.get_device_name(0) or getattr(_p, "name", "") or "").strip() or f"AMD GPU ({getattr(_p, 'gcnArchName', '')})"
print(f"Running on: {GPU}  |  ROCm {getattr(torch.version, 'hip', None)}  |  PyTorch {torch.__version__}")

CSV = "https://cdn.jsdelivr.net/gh/tannermundell/critto@main/scripts/sa_species_list.csv"
rows = list(csv.DictReader(io.StringIO(urllib.request.urlopen(CSV).read().decode())))
sci = [r["scientific_name"] for r in rows]; common = [r["common_name"] for r in rows]

model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")
tok = open_clip.get_tokenizer("hf-hub:imageomics/bioclip"); model = model.to(DEVICE).eval()
with torch.no_grad():
    tfeat = model.encode_text(tok([f"a photo of {n}" for n in sci]).to(DEVICE)); tfeat /= tfeat.norm(dim=-1, keepdim=True)
print(f"BioCLIP loaded on {GPU} — {len(rows)} South African species ready.")


# ==================== CELL 2 — the shot (film this) ====================
def identify(src, topk=3):
    raw = urllib.request.urlopen(src).read() if str(src).startswith("http") else open(src, "rb").read()
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    display(img.resize((320, int(320 * img.height / img.width))))
    x = preprocess(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        f = model.encode_image(x); f /= f.norm(dim=-1, keepdim=True)
        p = (model.logit_scale.exp() * f @ tfeat.T).squeeze(0).softmax(-1)
    print(f"Identified on {GPU} (ROCm):")
    for s, i in zip(*[t.tolist() for t in p.topk(topk)]):
        print(f"   {common[i]:26s} {s*100:5.1f}%")


# ==================== Test images (run after Cell 2) ====================
# A spread across birds, mammals, reptiles. Swap in your own photos with
# identify("yourfile.jpg") after dragging them into the Jupyter file panel.
TEST_IMAGES = {
    "Lion":            "https://inaturalist-open-data.s3.amazonaws.com/photos/9225318/medium.jpg",
    "Plains Zebra":    "https://inaturalist-open-data.s3.amazonaws.com/photos/335469754/medium.jpg",
    "African Elephant":"https://inaturalist-open-data.s3.amazonaws.com/photos/93674728/medium.jpg",
    "African Penguin": "https://static.inaturalist.org/photos/79056615/medium.jpg",
    "Common Ostrich":  "https://static.inaturalist.org/photos/2568822/medium.jpg",
    "Puff Adder":      "https://inaturalist-open-data.s3.amazonaws.com/photos/111121355/medium.jpeg",
    "Nile Crocodile":  "https://static.inaturalist.org/photos/545741360/medium.jpg",
    "Leopard Tortoise":"https://inaturalist-open-data.s3.amazonaws.com/photos/12902301/medium.jpg",
}
# Example: identify(TEST_IMAGES["Puff Adder"])
