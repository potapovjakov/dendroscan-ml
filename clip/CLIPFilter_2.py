import torch
from PIL import Image

import clip
from  clip.mobileclip import create_model_and_transforms, get_tokenizer

class CLIPFilter:
    def __init__(self, model_path: str, filters: dict, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model, _, self.preprocess = clip.mobileclip.create_model_and_transforms(
            'mobileclip_s1', pretrained=model_path
        )
        self.model = self.model.to(self.device).eval()
        self.tokenizer = clip.mobileclip.get_tokenizer('mobile/mobileclip_s1')

        self.filters = filters
        self.prompt_embeds = {}

        with torch.no_grad():
            for key, prompts in filters.items():
                tokens = self.tokenizer(prompts).to(self.device)
                text_features = self.model.encode_text(tokens)
                text_features /= text_features.norm(dim=-1, keepdim=True)
                self.prompt_embeds[key] = {
                    "labels": prompts,
                    "embeds": text_features
                }

    def process(self, image: Image.Image, problem_threshold=0.2):
        with torch.no_grad():
            img_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            image_features = self.model.encode_image(img_tensor)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            raw_results = {}
            problem_probs = {}

            for key, data in self.prompt_embeds.items():
                text_features = data["embeds"]
                probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)[0]

                if "problems" in key:
                    # сохраняем вероятности для всех проблемных классов
                    problem_probs[key] = {
                        data["labels"][i].replace("A photo of ", ""): float(probs[i])
                        for i in range(len(probs))
                    }
                else:

                    best_idx = probs.argmax().item()
                    label = data["labels"][best_idx].replace("A photo of ", "")
                    confidence = float(probs[best_idx])
                    raw_results[key] = {"label": label, "confidence": confidence}

            final_results = {}
            main_type = raw_results.get("tree or bush", {}).get("label", "").lower()
            if "tree" in main_type:
                final_results["type"] = "tree"
            elif "bush" in main_type:
                final_results["type"] = "bush"


            for key, value in raw_results.items():
                if key == "tree or bush":
                    continue
                if (final_results.get("type") == "tree" and "tree" in key) or \
                        (final_results.get("type") == "bush" and "bush" in key):
                    final_results[key] = value


            for key, probs_dict in problem_probs.items():
                if (final_results.get("type") == "tree" and "tree" in key) or \
                        (final_results.get("type") == "bush" and "bush" in key):
                    selected = [
                        k for k, v in probs_dict.items()
                        if v >= problem_threshold and "normal tree" not in k.lower() and "normal bush" not in k.lower()
                    ]
                    if not selected:
                        final_results[key] = None
                    elif len(selected) == 1:
                        final_results[key] = {
                            "label": selected[0],
                            "confidence": probs_dict[selected[0]]
                        }
                    else:
                        final_results[key] = [
                            {"label": s, "confidence": probs_dict[s]}
                            for s in selected
                        ]

            return final_results
