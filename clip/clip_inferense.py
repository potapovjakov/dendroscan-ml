import io

from clip import mobileclip
from PIL import Image
from clip.mobileclip.translate import translation_dict
import torch

filters = {
    "tree species": [
        "A photo of a Norway maple (Acer platanoides) tree.",
        "A photo of a Larch (Larix) tree.",
        "A photo of a Thuja (Thuja) tree.",
        "A photo of a Rowan (Sorbus) tree.",
        "A photo of a Birch (Betula) tree.",
        "A photo of a Chestnut (Castanea) tree.",
        "A photo of a Willow (Salix) tree.",
        "A photo of a Boxelder maple (Acer negundo) tree.",
        "A photo of an Aspen (Populus tremula) tree.",
        "A photo of a Linden (Tilia) tree.",
        "A photo of an Ash (Fraxinus) tree.",
        "A photo of an Oak (Quercus) tree.",
        "A photo of a Spruce (Picea) tree.",
        "A photo of a Pine (Pinus) tree.",
        "A photo of an Elm (Ulmus) tree.",
    ],
    "bush species": [
        "A photo of a Dwarf Scots pine (Pinus sylvestris f. fruticosa) bush.",
        "A photo of a Juniper (Juniperus) bush.",
        "A photo of a Shrubby cinquefoil (Pentaphylloides fruticosa) bush.",
        "A photo of a Mock-orange (Philadelphus) bush.",
        "A photo of a Common lilac (Syringa vulgaris) bush.",
        "A photo of a Siberian peashrub (Caragana arborescens) bush.",
        "A photo of a Ninebark (Physocarpus opulifolius) bush.",
        "A photo of a Spirea (Spiraea) bush.",
        "A photo of a Cotoneaster (Cotoneaster) bush.",
        "A photo of a Siberian dogwood (Cornus alba) bush.",
        "A photo of a Hazelnut (Corylus) bush.",
        "A photo of a Hawthorn (Crataegus) bush.",
        "A photo of a Dog rose (Rosa canina) bush.",
        "A photo of a Rugosa rose (Rosa rugosa) bush.",
    ],
    "tree or bush": [
        "A photo of a tree",
        "A photo of a bush",
    ],
    "tree problems": [
        "A photo of a tree showing example of the normal tree",
        "A photo of a tree showing example of the trunk rot",
        "A photo of a tree showing example of the cracks in the trunk",
        "A photo of a tree showing example of the trunk damage",
        "A photo of a tree showing example of the hollow in a tree",
        "A photo of a tree showing example of broken branches",
        "A photo of a tree showing example of dead branches",
        "A photo of a tree showing example of leaf spots or disease on leaves",
        "A photo of a tree showing example of insect damage on leaves",
        "A photo of a tree showing example of bark peeling",
        "A photo of a tree showing example of fungal growth on the trunk",
        "A photo of a tree showing example of mistletoe or parasitic plants",
        "A photo of a tree showing example of leaning or unstable trunk",
    ],
    "bush problems": [
        "A photo of a bush showing example of the normal bush",
        "A photo of a bush showing example of dead branches",
        "A photo of a bush showing example of broken branches",
        "A photo of a bush showing example of leaf spots or disease on leaves",
        "A photo of a bush showing example of insect damage on leaves",
        "A photo of a bush showing example of bark damage near the base",
        "A photo of a bush showing example of fungal growth",
        "A photo of a bush showing example of overgrown or untrimmed shape",
        "A photo of a bush showing example of dieback in branches",
        "A photo of a bush showing example of wilting leaves",
        "A photo of a bush showing example of parasitic plants or vines growing on it",
    ],
    "bush dry branches": [
        "A photo of a healthy bush with all green healthy branches",
        "A photo of a bush with green branches and several dried branches",
        "A photo of a bush with many dried branches",
        "A photo of a dead bush with all branches are dried",
    ],
    "tree is leaning": [
        "A photo of a straight tree",
        "A photo of a slightly leaning tree",
        "A photo of a significantly leaning tree",
    ],
}

problem_translation_dict = {
    # Tree problems
    "normal tree": None,
    "the trunk rot": "Гниль ствола",
    "the cracks in the trunk": "Трещины на стволе",
    "the trunk damage": "Повреждение ствола",
    "the hollow in a tree": "дупло",
    "broken branches": "сломанные ветви",
    "dead branches": "сухие ветви",
    "leaf spots or disease on leaves": "листовые пятна/болезни",
    "insect damage on leaves": "повреждение листьев насекомыми",
    "bark peeling": "шелушение коры",
    "fungal growth on the trunk": "грибковый налёт на стволе",
    "mistletoe or parasitic plants": "омела или паразитирующие растения",
    "leaning or unstable trunk": "наклонный или нестабильный ствол",
    "straight tree": "прямое дерево",
    "slightly leaning tree": "слегка наклонное дерево",
    "significantly leaning tree": "сильно наклонное дерево",
    # Bush problems
    "normal bush": None,
    "dead branches": "сухие ветви",
    "broken branches": "сломанные ветви",
    "leaf spots or disease on leaves": "листовые пятна/болезни",
    "insect damage on leaves": "повреждение листьев насекомыми",
    "bark damage near the base": "повреждение коры у основания",
    "fungal growth": "грибковый налёт",
    "overgrown or untrimmed shape": "переросший/неподрезанный куст",
    "dieback in branches": "отмирание ветвей",
    "wilting leaves": "вянут листья",
    "parasitic plants or vines growing on it": "паразитирующие растения или лианы",
    # Bush dry branches
    "healthy bush with all green healthy branches": "здоровый куст",
    "bush with green branches and several dried branches": "куст с зелёными и несколькими сухими ветвями",
    "bush with many dried branches": "куст с множеством сухих ветвей",
    "dead bush with all branches are dried": "сухой куст",
}


def clean_key(s: str) -> str:
    s = s.lower().replace(".", "").strip()

    if s.startswith("a photo of "):
        s = s[len("a photo of "):].strip()

    if s.startswith("a "):
        s = s[2:].strip()
    elif s.startswith("an "):
        s = s[3:].strip()

    if s.startswith("tree showing example of "):
        s = s[len("tree showing example of "):].strip()
    elif s.startswith("bush showing example of "):
        s = s[len("bush showing example of "):].strip()
    return s


def process_image(
        img: bytes,
        model,
        preprocess,
        tokenizer,
        translation_dict:dict,
        problem_translation_dict: dict,
        defect_threshold: float = 0.2,
) -> dict:
    image_input = preprocess(img).unsqueeze(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    image_input = image_input.to(device)

    # Разделяем классы
    species_texts = list(translation_dict.keys())
    defect_texts = list(problem_translation_dict.keys())
    all_texts = species_texts + defect_texts

    text_inputs = tokenizer(all_texts).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_inputs)

        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

    num_species = len(species_texts)
    species_scores = similarity[:, :num_species]
    best_prob, best_idx = species_scores[0].max(dim=-1)
    best_label = species_texts[best_idx]

    # --- Дефекты ---
    defect_scores = similarity[:, num_species:]
    top_probs, top_idx = torch.sort(defect_scores[0], descending=True)

    defects = []
    for prob, idx in zip(top_probs, top_idx):
        prob = float(prob)
        if prob < defect_threshold and len(defects) >= 1:
            break
        label = defect_texts[idx]
        ck = clean_key(label)
        translated_name = problem_translation_dict.get(ck, label)
        defects.append({
            "name": translated_name,
            "confidence": prob
        })

    ck = clean_key(best_label)
    name_ru, name_lat = translation_dict.get(ck, (best_label, ""))

    result = {
        "tree species": {
            "name": name_ru,
            "latin_name": name_lat,
            "confidence": float(best_prob)
        },
        "tree problems": defects
    }

    return result


def normalize_result(res: dict) -> dict:
    normalized = {}

    plant = res.get("tree species") or res.get("bush species") or {}
    normalized["plant"] = {
        "name": plant.get("name", "") if isinstance(plant, dict) else "",
        "latin_name": plant.get("latin_name", "") if isinstance(plant, dict) else "",
        "confidence": float(plant.get("confidence", 0.0)) if isinstance(plant, dict) else 0.0
    }

    defects = []
    ignore_list = {"слегка наклонное дерево", "прямое дерево", "здоровый куст"}

    possible_defect_keys = [
        "tree problems", "bush problems",
        "bush dry branches", "tree is leaning"
    ]

    for key in possible_defect_keys:
        val = res.get(key)
        if not val:
            continue

        if isinstance(val, list):
            for v in val:
                if isinstance(v, dict):
                    name = v.get("name") or v.get("problem") or v.get("label", "")
                    name = str(name).strip().lower()

                    # Пропускаем несущественные дефекты
                    if name in ignore_list:
                        continue

                    defects.append({
                        "name": name,
                        "confidence": float(v.get("confidence", 0.0))
                    })
                else:
                    name = str(v).strip().lower()
                    if name not in ignore_list:
                        defects.append({
                            "name": name,
                            "confidence": 0.0
                        })

        elif isinstance(val, dict):
            name = val.get("name") or val.get("problem") or val.get("label", "")
            name = str(name).strip().lower()
            if name not in ignore_list:
                defects.append({
                    "name": name,
                    "confidence": float(val.get("confidence", 0.0))
                })

        else:
            name = str(val).strip().lower()
            if name not in ignore_list:
                defects.append({
                    "name": name,
                    "confidence": 0.0
                })

    normalized["defects"] = defects

    return normalized


def get_clip_predict(crop_bytes):
    model, _, preprocess = mobileclip.create_model_and_transforms('mobileclip_s1', pretrained=None)
    tokenizer = mobileclip.get_tokenizer('mobileclip_s1')

    state_dict = torch.load("models/mobileclip_s1_finetuned.pt", map_location='cpu')
    model.load_state_dict(state_dict, strict=False)
    model.eval()

    img = Image.open(io.BytesIO(crop_bytes)).convert("RGB")
    result = process_image(img, model, preprocess, tokenizer, translation_dict, problem_translation_dict, defect_threshold=0.1)
    norm_result = normalize_result(result)

    return norm_result
