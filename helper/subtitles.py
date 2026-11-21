def language_text(Subtitle):
    return f"{Subtitle.get('DisplayTitle', '')} {Subtitle.get('language', '')}".lower()

def is_default(Subtitle):
    return Subtitle.get('Default', False) or Subtitle.get('default', False) or "(default" in Subtitle.get('DisplayTitle', '').lower()

def is_default_ass(Subtitle):
    return is_default(Subtitle) and Subtitle.get('Codec', '').lower() in ("ass", "ssa")

def is_forced(Subtitle):
    return Subtitle.get('Forced', False) or "forced" in Subtitle.get('DisplayTitle', '').lower()

def is_chinese(Subtitle):
    Text = language_text(Subtitle)
    return any(Marker in Text for Marker in ("chinese", "中文", "汉语", "漢語", "mandarin", "zho")) or Text.startswith("zh") or " zh" in Text or "zh-" in Text or "zh_" in Text or Text.endswith(" chi") or "chi-" in Text or "chi_" in Text

def is_simplified_chinese(Subtitle):
    Text = language_text(Subtitle)
    return any(Marker in Text for Marker in ("simplified", "简体", "简中", "简体中文", "chs", "zh-cn", "zh_cn", "zh-hans", "zhhans"))

def is_traditional_chinese(Subtitle):
    Text = language_text(Subtitle)
    return any(Marker in Text for Marker in ("traditional", "繁體", "繁体", "繁體中文", "繁体中文", "cht", "zh-tw", "zh_tw", "zh-hant", "zhhant"))

def matches_preference(Subtitle, SubtitlesLanguageDefault):
    Title = Subtitle.get('DisplayTitle', '').lower()
    Language = Subtitle.get('language', '').lower()
    return bool(SubtitlesLanguageDefault) and (SubtitlesLanguageDefault in Title or SubtitlesLanguageDefault in Language or (SubtitlesLanguageDefault == "forced_only" and is_forced(Subtitle)))

def get_PreferredSubtitle(SubtitleStreams, SubtitlesLanguageDefault):
    Preference = SubtitlesLanguageDefault.lower()
    ChinesePreference = any(Marker in Preference for Marker in ("chinese", "中文", "汉语", "漢語", "mandarin", "zho")) or Preference.startswith("zh") or "zh-" in Preference or "zh_" in Preference or Preference == "chi"
    TraditionalPreference = any(Marker in Preference for Marker in ("traditional", "繁體", "繁体", "cht", "zh-tw", "zh_tw", "zh-hant", "zhhant"))
    PreferredSubtitle = None

    if ChinesePreference:
        if TraditionalPreference:
            FirstChinese = is_traditional_chinese
        else:
            FirstChinese = is_simplified_chinese

        PreferredSubtitle = next((Subtitle for Subtitle in SubtitleStreams if Subtitle['external'] and FirstChinese(Subtitle)), None)
        PreferredSubtitle = PreferredSubtitle or next((Subtitle for Subtitle in SubtitleStreams if not Subtitle['external'] and FirstChinese(Subtitle)), None)
        PreferredSubtitle = PreferredSubtitle or next((Subtitle for Subtitle in SubtitleStreams if Subtitle['external'] and is_chinese(Subtitle)), None)
        PreferredSubtitle = PreferredSubtitle or next((Subtitle for Subtitle in SubtitleStreams if not Subtitle['external'] and is_chinese(Subtitle)), None)

    if not PreferredSubtitle:
        PreferredSubtitle = next((Subtitle for Subtitle in SubtitleStreams if Subtitle['external'] and is_default_ass(Subtitle)), None)
        PreferredSubtitle = PreferredSubtitle or next((Subtitle for Subtitle in SubtitleStreams if not Subtitle['external'] and is_default_ass(Subtitle)), None)
        PreferredSubtitle = PreferredSubtitle or next((Subtitle for Subtitle in SubtitleStreams if Subtitle['external'] and is_default(Subtitle)), None)
        PreferredSubtitle = PreferredSubtitle or next((Subtitle for Subtitle in SubtitleStreams if not Subtitle['external'] and is_default(Subtitle)), None)
        PreferredSubtitle = PreferredSubtitle or next((Subtitle for Subtitle in SubtitleStreams if Subtitle['external'] and matches_preference(Subtitle, SubtitlesLanguageDefault)), None)
        PreferredSubtitle = PreferredSubtitle or next((Subtitle for Subtitle in SubtitleStreams if not Subtitle['external'] and matches_preference(Subtitle, SubtitlesLanguageDefault)), None)

    return PreferredSubtitle, ChinesePreference

def is_LanguagePreferred(PreferredSubtitle, SubtitlesLanguageDefault, ChinesePreference):
    if not PreferredSubtitle or not SubtitlesLanguageDefault:
        return False

    return matches_preference(PreferredSubtitle, SubtitlesLanguageDefault) or (ChinesePreference and is_chinese(PreferredSubtitle))
