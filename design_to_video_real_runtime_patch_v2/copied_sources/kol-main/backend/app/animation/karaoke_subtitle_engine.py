from __future__ import annotations
import html, re
from dataclasses import dataclass
@dataclass(slots=True)
class WordTiming:
    word: str
    start: float
    end: float
class KaraokeSubtitleEngine:
    def build_word_timings(self, text: str, duration: float, speech_marks: list[dict] | None = None) -> list[WordTiming]:
        if speech_marks:
            timings=[]
            for mark in speech_marks:
                word=str(mark.get("word") or mark.get("text") or "").strip()
                if word:
                    start=float(mark.get("start", mark.get("time", 0))); end=float(mark.get("end", start+0.25))
                    timings.append(WordTiming(word, start, max(end, start+0.08)))
            if timings: return timings
        words=[w for w in re.split(r"\s+", text.strip()) if w]
        if not words: return []
        step=max(0.12, duration / len(words))
        return [WordTiming(w, round(i*step,3), round((i+1)*step,3)) for i,w in enumerate(words)]
    def to_srt(self, word_timings: list[WordTiming], words_per_line: int = 5) -> str:
        blocks=[]
        for idx in range(0, len(word_timings), words_per_line):
            group=word_timings[idx:idx+words_per_line]
            if group: blocks.append(f"{len(blocks)+1}\n{self._ts(group[0].start)} --> {self._ts(group[-1].end)}\n{' '.join(w.word for w in group)}\n")
        return "\n".join(blocks)
    def to_ass(self, word_timings: list[WordTiming], style: dict | None = None) -> str:
        style=style or {}; font_size=int(style.get("font_size",64)); primary=style.get("primary","&H00FFFFFF"); highlight=style.get("highlight","&H0000FFFF")
        header=f"""[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Karaoke,Arial,{font_size},{primary},{highlight},&H00111111,&H80000000,-1,0,0,0,100,100,0,0,1,5,1,2,80,80,260,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"""
        lines=[]
        for idx in range(0, len(word_timings), 5):
            group=word_timings[idx:idx+5]
            if group:
                karaoke="".join(f"{{\\k{max(1,int((w.end-w.start)*100))}}}{html.escape(w.word)} " for w in group)
                lines.append(f"Dialogue: 0,{self._ass_ts(group[0].start)},{self._ass_ts(group[-1].end)},Karaoke,,0,0,0,,{karaoke.strip()}")
        return header+"\n".join(lines)+"\n"
    def _ts(self, seconds: float) -> str:
        ms=int(round(seconds*1000)); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000); return f"{h:02}:{m:02}:{s:02},{ms:03}"
    def _ass_ts(self, seconds: float) -> str:
        cs=int(round(seconds*100)); h,cs=divmod(cs,360000); m,cs=divmod(cs,6000); s,cs=divmod(cs,100); return f"{h}:{m:02}:{s:02}.{cs:02}"
