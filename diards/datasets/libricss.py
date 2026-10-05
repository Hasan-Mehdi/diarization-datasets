"""LibriCSS (Microsoft; LibriSpeech-derived, CC BY 4.0): SIMULATED meetings re-recorded in a real room.

LibriSpeech utterances of 8 speakers were concatenated into ~10-minute "sessions" with a target overlap ratio
(0L/0S = no overlap with long/short silences, OV10..OV40 = 10-40% overlap), played through loudspeakers in a
meeting room and recorded with a 7-channel array. The reference is therefore exact by construction (start/end of
each played utterance), but it marks whole LibriSpeech utterances, including their leading/trailing silence and
internal pauses, and the "conversation" has no real turn-taking dynamics. Clearly marked **synthetic**.

Views: ``sdm`` (default) = channel 0 of the room recording; ``clean-mix`` = the original digital mixture.
Splits: ``dev`` = session0 of each condition, ``eval`` = sessions 1-9 (the convention of the LibriCSS papers).
Speaker ids: LibriSpeech speaker ids (global). UEM: whole session.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

from ..annotation import Segment
from ..audio import convert, is_normalized
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter

GDRIVE = "1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l"
CONDITIONS = ["0L", "0S", "OV10", "OV20", "OV30", "OV40"]

META = DatasetMeta(
    name="libricss",
    title="LibriCSS (re-recorded simulated meetings) - SYNTHETIC",
    homepage="https://github.com/chenzhuo1011/libri_css",
    license="CC-BY-4.0 (LibriSpeech-derived)",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    annotation_redistributable=True,
    citation="Z. Chen et al., 'Continuous speech separation: dataset and analysis', ICASSP 2020.",
    source_version="for_release.zip (Google Drive id 1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l)",
    description="10 h: 60 sessions x ~10 min, 8 LibriSpeech speakers each, utterances replayed by loudspeakers in a meeting room.",
    access="Free download (Google Drive, 6.4 GB).",
    reference="Exact playback times of each LibriSpeech utterance (by construction).",
    default_view="sdm",
    views={"sdm": "Channel 0 of the 7-channel room recording", "clean-mix": "Original digital mixture before playback"},
    gt_rating="S (synthetic)",
    gt_rating_reason=("Timing is exact by construction but covers whole read-speech utterances (with their silences); "
                      "no natural turn-taking, backchannels or laughter; useful for controlled overlap studies only."),
    choices=["Splits: dev = session0, eval = sessions 1-9.", "Speaker ids: LibriSpeech speaker ids.",
             "UEM: whole session.", "Condition (0L/0S/OV10-OV40) in manifest extra."],
    domain="synthetic meetings (read speech replayed in a room)",
)


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "libricss"
    z = base / "for_release.zip"
    if not z.exists():
        import gdown

        gdown.download(id=GDRIVE, output=str(z), quiet=False)
    rel = base / "for_release"
    if not rel.exists():
        with zipfile.ZipFile(z) as zf:
            zf.extractall(base)
    views = views or list(META.views)
    w = DatasetWriter(META, root)
    n = 0
    for cond in CONDITIONS:
        for sess in sorted((rel / cond).iterdir()):
            if not sess.is_dir():
                continue
            parts = sess.name.split("_")
            name = next(p for p in parts if p.startswith("session"))
            split = "dev" if name == "session0" else "eval"
            if splits and split not in splits:
                continue
            if limit and n >= limit:
                break
            n += 1
            oid = f"{cond}_{name}"
            sid = w.session_id(oid)
            audio = {}
            if "sdm" in views:
                dst = w.audio_path(sid, "sdm")
                if not is_normalized(dst):
                    convert(sess / "record" / "raw_recording.wav", dst, channel=0)
                audio["sdm"] = dst
            if "clean-mix" in views:
                dst = w.audio_path(sid, "clean-mix")
                if not is_normalized(dst):
                    convert(sess / "clean" / "mix.wav", dst)
                audio["clean-mix"] = dst
            segs = []
            for line in (sess / "transcription" / "meeting_info.txt").read_text(encoding="utf-8").splitlines():
                p = line.split("\t")
                if len(p) < 3:
                    continue
                try:
                    a, b = float(p[0]), float(p[1])
                except ValueError:
                    continue  # header
                segs.append(Segment(a, b, p[2]))
            w.add_session(oid, split, segs, audio=audio, extra={"condition": cond, "folder": sess.name})
            print(f"  [libricss] {split} {oid} ok", flush=True)
    w.finalize([{"url": f"https://drive.google.com/file/d/{GDRIVE}"}])
