import io
from settings import logger
from PIL import Image
from clip.CLIPFilter_2 import CLIPFilter
from clip.mobileclip.translate import translation_dict
from settings import logger

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
        s = s[len("a photo of ") :].strip()

    if s.startswith("a "):
        s = s[2:].strip()
    elif s.startswith("an "):
        s = s[3:].strip()

    if s.startswith("tree showing example of "):
        s = s[len("tree showing example of ") :].strip()
    elif s.startswith("bush showing example of "):
        s = s[len("bush showing example of ") :].strip()
    return s


def process_image(
    img,
        clf,
        translation_dict: dict,
        problem_translation_dict: dict,
) -> dict:
    result = clf.process(img)

    translated_result = {}
    for key, value in result.items():
        if key == "type":
            translated_result[key] = value
            continue

        if isinstance(value, list):
            translated_result[key] = []
            for v in value:
                if isinstance(v, dict):
                    label = v["label"]
                    conf = v["confidence"]
                    ck = clean_key(label)
                    translated_result[key].append(
                        {
                            "problem": problem_translation_dict.get(ck, label),
                            "confidence": conf,
                        }
                    )
                else:
                    # fallback если вернулась строка
                    translated_result[key].append(
                        problem_translation_dict.get(clean_key(v), v)
                    )

        elif isinstance(value, dict):
            label = value["label"]
            conf = value["confidence"]
            ck = clean_key(label)

            if key in ["tree species", "bush species"]:
                name_ru, name_lat = translation_dict.get(ck, (label, ""))
                translated_result[key] = {
                    "name": name_ru,
                    "latin_name": name_lat,
                    "confidence": conf,
                }

            elif ck in problem_translation_dict:
                translated_result[key] = {
                    "name": problem_translation_dict[ck],
                    "confidence": conf,
                }

            else:
                translated_result[key] = {"label": label, "confidence": conf}

        elif isinstance(value, str):
            ck = clean_key(value)
            translated_result[key] = translation_dict.get(ck, (value, ""))

        else:
            translated_result[key] = None

    return translated_result

def normalize_result(res: dict) -> dict:
    normalized = {}
    plant = res.get("tree species") or res.get("bush species") or {}

    normalized["plant"] = {
        "name": plant.get("name", "") if isinstance(plant, dict) else "",
        "latin_name": plant.get("latin_name", "") if isinstance(plant, dict) else "",
        "confidence": float(plant.get("confidence", 0.0))
        if isinstance(plant, dict)
        else 0.0,
    }

    plant_type = res.get("type")
    if plant_type == "tree":
        normalized["plant"]["type"] = "Дерево"
    elif plant_type == "bush":
        normalized["plant"]["type"] = "Куст"
    else:
        normalized["plant"]["type"] = ""

    defects = []
    skip_names = [
        "здоровый куст",
        "прямое дерево",
        "слегка наклонное дерево",
        "переросший/неподрезанный куст",
    ]

    for key in [
        "tree problems",
        "bush problems",
        "bush dry branches",
        "tree is leaning",
    ]:
        val = res.get(key)
        logger.info(f"Processing {key}: {val}")

        if not val:
            continue

        if isinstance(val, dict) and val.get("name") in skip_names:
            continue
        if isinstance(val, str) and val in skip_names:
            continue

        if isinstance(val, list):
            for v in val:
                if isinstance(v, dict):
                    name = v.get("name") or v.get("problem") or v.get("label", "")
                    if name in skip_names:
                        continue
                    defects.append({
                        "name": name,
                        "confidence": float(v.get("confidence", 0.0)),
                    })
                else:
                    if str(v) in skip_names:
                        continue
                    defects.append({"name": str(v), "confidence": 0.0})

        elif isinstance(val, dict):
            name = val.get("name") or val.get("problem") or val.get("label", "")
            if name in skip_names:
                continue
            defects.append({
                "name": name,
                "confidence": float(val.get("confidence", 0.0)),
            })

        else:
            if str(val) in skip_names:
                continue
            defects.append({"name": str(val), "confidence": 0.0})

    normalized["plant"]["defects"] = defects
    logger.info(f"normalized result: {normalized}")

    return normalized


def get_clip_predict(crop_bytes):
    clf = CLIPFilter("models/mobileclip_s1.pt", filters)
    img = Image.open(io.BytesIO(crop_bytes)).convert("RGB")
    result = process_image(img, clf, translation_dict, problem_translation_dict)
    norm_result = normalize_result(result)
    return norm_result


