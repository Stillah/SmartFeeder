import io
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn


class ArcMarginProduct(nn.Module):
    def __init__(self, in_features, out_features, s=64.0, m=0.3):
        super().__init__()
        self.weight = nn.Parameter(torch.FloatTensor(out_features, in_features))
        nn.init.xavier_normal_(self.weight)
        self.s = s
        self.m = m

    def forward(self, features, targets):
        # Not used during inference
        raise NotImplementedError


class CatNetModel(nn.Module):
    def __init__(
        self,
        backbone_name="resnet152",
        num_classes=1000,
        embedding_size=2560,
        use_arcface=False,
    ):
        super().__init__()
        if backbone_name == "resnet152":
            backbone = models.resnet152(weights=None)
        elif backbone_name == "resnet101":
            backbone = models.resnet101(weights=None)
        elif backbone_name == "resnet50":
            backbone = models.resnet50(weights=None)
        else:
            raise ValueError(f"Unknown backbone: {backbone_name}")
        self.backbone = nn.Sequential(*list(backbone.children())[:-1])
        num_filters = backbone.fc.in_features
        self.adaptor = nn.Linear(num_filters, embedding_size)
        self.bn = nn.BatchNorm1d(embedding_size)
        self.embedding_fc = nn.utils.weight_norm(
            nn.Linear(embedding_size, embedding_size, bias=False), name="weight"
        )
        self.final_fc = nn.utils.weight_norm(
            nn.Linear(embedding_size, num_classes, bias=False), name="weight"
        )
        self.use_arcface = use_arcface
        if use_arcface:
            self.arcface_layer = ArcMarginProduct(embedding_size, num_classes)

    def forward(self, x):
        features = self.backbone(x)
        features = features.flatten(1)
        out = self.adaptor(features)
        out = self.bn(out)
        out = self.embedding_fc(out)
        embedding = F.normalize(out, p=2, dim=1)
        return embedding


class ResizePad:
    def __init__(self, target_size):
        self.target_size = target_size

    def __call__(self, img):
        w, h = img.size
        scale = self.target_size / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        pad_w = self.target_size - new_w
        pad_h = self.target_size - new_h
        padding = (pad_w // 2, pad_h // 2, pad_w - (pad_w // 2), pad_h - (pad_h // 2))
        return transforms.functional.pad(img, padding, fill=0, padding_mode="constant")


MODEL_PATH = "model/best_ppgnnet_cat.pth"
BACKBONE = "resnet152"
EMBEDDING_SIZE = 2560
USE_ARCFACE = False  # must match training config
IMG_SIZE = 224

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CatNetModel(
    backbone_name=BACKBONE,
    num_classes=1,  # dummy, not used for inference
    embedding_size=EMBEDDING_SIZE,
    use_arcface=USE_ARCFACE,
)
# Load checkpoint, but skip classifier-related keys
state_dict = torch.load(MODEL_PATH, map_location=device, weights_only=True)

# Filter out 'final_fc' and 'arcface_layer' keys
filtered_state_dict = {}
for k, v in state_dict.items():
    if not (k.startswith("final_fc") or k.startswith("arcface_layer")):
        filtered_state_dict[k] = v

missing_keys, unexpected_keys = model.load_state_dict(filtered_state_dict, strict=False)
print(f"Missing keys (expected): {missing_keys}")
print(f"Unexpected keys (ignored): {unexpected_keys}")

model.to(device)
model.eval()

transform = transforms.Compose(
    [
        ResizePad(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


app = FastAPI(title="CatNet Embedding Service")


@app.post("/embedding")
async def get_embedding(file: UploadFile = File(...)):
    # Read and preprocess image
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = model(img_tensor)

    # Return as list of floats
    return JSONResponse(content={"embedding": embedding.cpu().numpy().tolist()[0]})


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
