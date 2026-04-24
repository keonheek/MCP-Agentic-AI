"""
Layer 3: 자막 추출 + Claude로 하이라이트 구간 선별
해외 영상의 핵심 30초 이내 클립 3-5개 (Fair Use 한도)
"""
import json
import os
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).resolve().parents[4]


def extract_transcript(video_path: str, language: str = "en") -> list[dict]:
    """faster-whisper 자막 추출"""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return []

    model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(
            video_path, language=language if language != "auto" else None,
            beam_size=5, vad_filter=True,
        )
        return [
            {"start": seg.start, "end": seg.end, "text": seg.text.strip()}
            for seg in segments
        ]
    except Exception as e:
        print(f"[WARN] Whisper 추출 실패: {e}")
        return []


def extract_highlights(transcript: list[dict], max_highlights: int = 4) -> list[dict]:
    """Claude로 하이라이트 구간 선별 (각 30초 이내)"""
    if not transcript:
        return []

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    full_text = "\n".join(
        f"[{s['start']:.1f}-{s['end']:.1f}] {s['text']}"
        for s in transcript
    )

    prompt = f"""다음은 해외 AI 영상의 영어 자막이야.
한국어 번역 롱폼 컨텐츠를 만들기 위해 **Fair Use 범위 내** 핵심 구간을 {max_highlights}개 선별해.

조건:
- 각 구간은 30초 이내 (Fair Use 보호 범위)
- 핵심 메시지 (주장/발표/결론) 우선
- 시작-종료 시간 초 단위 명시

자막:
{full_text[:4000]}

JSON 배열만 출력:
[
  {{"start": 12.5, "end": 38.0, "summary_ko": "한국어 요약", "importance": "high|medium"}},
  ...
]"""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        start = text.find("[")
        end = text.rfind("]") + 1
        highlights = json.loads(text[start:end])
        return highlights
    except Exception as e:
        print(f"[WARN] 하이라이트 추출 실패: {e}")
        return []


def process(video_path: str, language: str = "en") -> dict:
    """자막 추출 + 하이라이트 + 저장"""
    transcript = extract_transcript(video_path, language)
    highlights = extract_highlights(transcript)

    output_path = Path(video_path).with_suffix(".highlights.json")
    result = {
        "video_path": video_path,
        "transcript": transcript,
        "highlights": highlights,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[Highlight] 자막 {len(transcript)} / 하이라이트 {len(highlights)}개 → {output_path}")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python highlight_extractor.py <video_path>")
        sys.exit(1)
    process(sys.argv[1])
