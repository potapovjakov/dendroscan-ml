import torch
from PIL import Image
from  clip.mobileclip import create_model_and_transforms, get_tokenizer

class CLIPFilter:
    def __init__(self, model_path: str, filters: dict, translations: dict, latin_names: dict, device=None):
        """
        model_path: путь до модели (например, "mobileclip_s1.pt")
        filters: словарь с классами {"plants": [...], "defects": [...]}
        translations: словарь переводов EN -> RU
        latin_names: словарь с латинскими названиями растений
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model, _, self.preprocess = create_model_and_transforms(
            'mobileclip_s1', pretrained=model_path
        )
        self.model = self.model.to(self.device).eval()
        self.tokenizer = get_tokenizer('mobileclip_s1')

        self.filters = filters
        self.translations = translations
        self.latin_names = latin_names
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

    def process(self, image: Image.Image, threshold: float = 0.2):
        """
        Обрабатывает изображение и возвращает результат:
        {
            "plants": { "name", "latin_name", "confidence" },
            "defects": [
                { "name", "confidence" },
                ...
            ]
        }
        """
        result = {}
        with torch.no_grad():
            img_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            image_features = self.model.encode_image(img_tensor)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            # ----- plants (один лучший вариант)
            data = self.prompt_embeds["plants"]
            text_features = data["embeds"]
            probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)[0]

            best_idx = probs.argmax().item()
            label_en = data["labels"][best_idx]
            label_ru = self.translations.get(label_en, label_en)
            latin_name = self.latin_names.get(label_en, "")
            confidence = probs[best_idx].item()

            result["plant"] = {
                "name": label_ru,
                "latin_name": latin_name,
                "confidence": round(confidence, 3)
            }

            # ----- defects (несколько по threshold)
            data = self.prompt_embeds["defects"]
            text_features = data["embeds"]
            probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)[0]

            problem_list = []
            for i, p in enumerate(probs):
                if p.item() >= threshold:
                    label_en = data["labels"][i]
                    label_ru = self.translations.get(label_en, label_en)
                    problem_list.append({
                        "name": label_ru,
                        "confidence": round(p.item(), 3)
                    })

            # если ни один не прошёл threshold — берём максимум
            if not problem_list:
                best_idx = probs.argmax().item()
                label_en = data["labels"][best_idx]
                label_ru = self.translations.get(label_en, label_en)
                problem_list.append({
                    "name": label_ru,
                    "confidence": round(probs[best_idx].item(), 3)
                })

            result["plant"]["defects"] = problem_list

        return result
