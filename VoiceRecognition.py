import whisper


def recognition(destination_file: str, model: str = "small"):
    #validation model name
    model = "base" if model not in ['tiny', 'base', 'small', 'medium', 'large'] else model
    print(f"using {model} model")
    model = whisper.load_model(model)
    result = model.transcribe(destination_file, language="ru", fp16=False)
    return result["text"]


def split_string(s, chunk_size=4096):
    for start in range(0, len(s), chunk_size):
        yield s[start:start + chunk_size]


# model = whisper.load_model("large-v3")
# result = model.transcribe("voice/5631.ogg", language="ru", fp16=False,  verbose=True)
# print(result["text"])
