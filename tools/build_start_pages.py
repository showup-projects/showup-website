#!/usr/bin/env python3
"""Build the Getting Started pages: start/<page>.html, -ko.html and -de.html.

Five pages (solo, group, gym, program, member) in three languages. The welcome
email and the "Showup이 새롭게 단장했어요" email link here, one card per page.
The same five guides also go into the Help Center (help.html, -ko, -de) as
articles in their own sidebar group, and a banner at the top of the Welcome
article links to them with the welcome email's five cards; all between
generated markers.

This file is the single source of truth for those pages: their copy, which
screenshots each step shows, and the markup. To change a page, edit COPY or
STEPS below and run

    python3 tools/build_start_pages.py
    python3 tools/sync_footer.py

The second command stamps the shared footer into the pages (they are listed in
its PAGES table). Hand edits to start/*.html are overwritten on the next run.

Screenshots: assets/screenshots/<ko|en>/<name>[-dark].webp. Korean pages use
the ko set; English and German pages use the en set, like the rest of the site.
"""

import html
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "start"
SITE = "https://www.showupcounts.com"

APP_STORE_URL = "https://apps.apple.com/app/showup-it-counts/id6761016399"
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.showup.showupAndroid"

LANGS = ["en", "ko", "de"]
PAGE_ORDER = ["solo", "group", "gym", "program", "member"]


def suffix(lang):
    return "" if lang == "en" else "-" + lang


def shot_dir(lang):
    return "ko" if lang == "ko" else "en"


# ---------------------------------------------------------------------------
# Which screenshots each step shows, in order. Names are files in
# assets/screenshots/<lang>/ without ".webp"; each also has a "-dark" twin.
# A step with no screenshot uses an empty list.
# ---------------------------------------------------------------------------
STEPS = {
    "solo": {
        "start": [["start-purpose"], ["start-add-workout"], ["start-add-score"],
                  ["personal-records", "pr-detail"], ["start-home"]],
        "more": [["start-percent-detail"], []],
    },
    "group": {
        "start": [["start-purpose"], ["workouts"], ["start-space-qr", "start-join-request"],
                  ["leaderboard", "scores"], ["community"]],
        "more": [["start-pr-board"], ["collab"]],
    },
    "gym": {
        "start": [["start-purpose"], ["start-invite-member"],
                  ["start-schedule-workout", "start-pending-week"],
                  ["start-add-schedule", "booking", "booking-detail"],
                  ["start-space-qr", "start-members"]],
        "more": [["start-percent-week", "start-space-exercises"],
                 ["start-membership-plans", "start-holds"],
                 ["leaderboard", "community"], ["collab"]],
    },
    "program": {
        "start": [["start-purpose"], ["start-schedule-workout", "start-pending-week"],
                  ["start-percent-week", "start-space-exercises"],
                  ["start-space-qr", "start-membership-plans"], ["leaderboard", "scores"]],
        "more": [["collab"], ["start-media-library"]],
    },
    "member": {
        # The in-app QR scan shot (taken on a real iPhone) goes first here once it exists.
        "start": [["start-home-invite"], ["workout-detail", "start-add-score"],
                  ["personal-records", "start-percent-detail"], ["booking", "booking-detail"]],
        "more": [["leaderboard"], ["start-my-membership"], [], ["community"]],
    },
}

# Alt text for every screenshot, per language.
ALT = {
    "start-purpose": {"ko": "스페이스 용도를 고르는 화면", "en": "Choosing what the space is for", "de": "Auswahl, wofür der Space gedacht ist"},
    "start-add-workout": {"ko": "운동 추가 화면의 점수 기록 방식", "en": "Add Workout with its scoring options", "de": "Workout hinzufügen mit den Wertungsarten"},
    "start-add-score": {"ko": "세트마다 무게를 적은 내 점수 추가 화면", "en": "Add My Score with a weight for each set", "de": "Mein Ergebnis hinzufügen mit einem Gewicht pro Satz"},
    "personal-records": {"ko": "PR 목록", "en": "Personal records", "de": "Persönliche Rekorde"},
    "pr-detail": {"ko": "PR 기록 차트", "en": "Personal record chart", "de": "Diagramm eines persönlichen Rekords"},
    "start-home": {"ko": "Showup 카드와 내 스페이스가 보이는 홈", "en": "Home with the Showup card and My Spaces", "de": "Start mit der Showup-Karte und Meine Spaces"},
    "start-percent-detail": {"ko": "PR로 계산된 무게가 보이는 운동", "en": "A workout showing weights worked out from PRs", "de": "Ein Workout mit Gewichten, berechnet aus PRs"},
    "start-percent-week": {"ko": "PR로 계산된 무게가 보이는 주간 운동", "en": "The week's workouts with weights worked out from PRs", "de": "Workouts der Woche mit Gewichten, berechnet aus PRs"},
    "workouts": {"ko": "주간 운동 캘린더", "en": "Weekly workout calendar", "de": "Wöchentlicher Workout-Kalender"},
    "start-space-qr": {"ko": "스페이스 QR 코드", "en": "Space QR code", "de": "QR-Code des Space"},
    "start-join-request": {"ko": "가입 요청 수락 화면", "en": "A join request with Accept Request", "de": "Eine Beitrittsanfrage mit Anfrage annehmen"},
    "leaderboard": {"ko": "운동 리더보드", "en": "Workout leaderboard", "de": "Workout-Rangliste"},
    "scores": {"ko": "점수 상세와 댓글", "en": "Score detail with comments", "de": "Ergebnisdetails mit Kommentaren"},
    "community": {"ko": "커뮤니티 피드", "en": "Community feed", "de": "Community-Feed"},
    "start-pr-board": {"ko": "종목별 순위가 보이는 PR 보드", "en": "PR Board with a ranking for each lift", "de": "PR-Tafel mit einer Rangfolge je Übung"},
    "collab": {"ko": "콜라보 운동", "en": "Collaborative workout", "de": "Kollaboratives Workout"},
    "start-invite-member": {"ko": "역할을 코치로 고른 멤버 초대 화면", "en": "Invite Member with the Coach role", "de": "Mitglied einladen mit der Rolle Trainer"},
    "start-schedule-workout": {"ko": "운동 공개 예약 시간을 정하는 화면", "en": "Setting a release time under Schedule workout", "de": "Freigabezeit unter Workout planen festlegen"},
    "start-pending-week": {"ko": "공개 전 운동이 점선 카드로 보이는 주간 화면", "en": "Week view with a scheduled workout in a dashed card", "de": "Wochenansicht mit einem geplanten Workout in gestrichelter Karte"},
    "start-add-schedule": {"ko": "매주 반복, 정원, 코치를 정한 일정 추가 화면", "en": "Add Schedule with a weekly repeat, capacity and coach", "de": "Termin hinzufügen mit wöchentlicher Wiederholung, Kapazität und Coach"},
    "booking": {"ko": "수업 예약 주간 화면", "en": "Class booking week view", "de": "Wochenansicht der Kursbuchung"},
    "booking-detail": {"ko": "예약할 수 있는 수업 상세", "en": "Class detail with booking", "de": "Kursdetails mit Buchung"},
    "start-members": {"ko": "남은 기간과 홀딩이 보이는 멤버 목록", "en": "Member list with days left and holds", "de": "Mitgliederliste mit Restlaufzeit und Pausen"},
    "start-space-exercises": {"ko": "스페이스 운동 목록", "en": "Space Exercises", "de": "Space-Übungen"},
    "start-membership-plans": {"ko": "멤버십 플랜 목록", "en": "Membership plans", "de": "Mitgliedschaftspläne"},
    "start-holds": {"ko": "홀딩 내역", "en": "Hold history", "de": "Verlauf der Pausen"},
    "start-media-library": {"ko": "미디어 라이브러리", "en": "Media Library", "de": "Medienbibliothek"},
    "start-home-invite": {"ko": "홈에 온 스페이스 초대", "en": "A space invitation on Home", "de": "Eine Space-Einladung im Tab Start"},
    "workout-detail": {"ko": "오늘의 운동", "en": "Today's workout", "de": "Heutiges Workout"},
    "start-my-membership": {"ko": "남은 기간과 홀딩이 보이는 내 멤버십", "en": "My Membership with its dates and holds", "de": "Meine Mitgliedschaft mit Laufzeit und Pausen"},
}

# ---------------------------------------------------------------------------
# Copy. Items are (title, body). **x** becomes <strong>x</strong>; [text](url)
# becomes a link. Everything else is escaped.
# ---------------------------------------------------------------------------
COMMON = {
    "ko": {
        "start": "시작하기",
        "more": "익숙해지면",
        "start_note": "새로 가입했다면 홈의 **시작하기**도 같은 순서로 안내해요.",
        "open": "Showup 열기",
        "others": "다른 용도 보기",
        "others_member": "내 스페이스를 직접 만들고 싶다면",
        "title": "{name} — Showup 시작하기",
        "lang_label": "KR",
    },
    "en": {
        "start": "Getting Started",
        "more": "When you're ready for more",
        "start_note": "If you just signed up, **Getting Started** on the Home tab walks you through the same steps.",
        "open": "Open Showup",
        "others": "Other ways to use Showup",
        "others_member": "Want a space of your own?",
        "title": "{name} — Getting started with Showup",
        "lang_label": "EN",
    },
    "de": {
        "start": "Erste Schritte",
        "more": "Wenn du so weit bist",
        "start_note": "Bist du neu dabei, führt dich **Erste Schritte** im Tab Start durch dieselben Schritte.",
        "open": "Showup öffnen",
        "others": "Showup anders nutzen",
        "others_member": "Lieber einen eigenen Space?",
        "title": "{name} — Erste Schritte mit Showup",
        "lang_label": "DE",
    },
}

NAMES = {
    "ko": {"solo": "혼자 사용", "group": "소규모 그룹", "gym": "체육관 또는 박스", "program": "트레이닝 프로그램", "member": "초대받아 들어왔어요"},
    "en": {"solo": "Just for me", "group": "Small group", "gym": "Gym or Box", "program": "Training program", "member": "I was invited"},
    "de": {"solo": "Nur für mich", "group": "Kleine Gruppe", "gym": "Gym oder Box", "program": "Trainingsprogramm", "member": "Ich wurde eingeladen"},
}

COPY = {
    # ------------------------------------------------------------------ ko
    "ko": {
        "solo": {
            "title": "나만의 운동 일지, 이제 Showup에 쌓아요",
            "subtitle": "운동을 올리고, 기록하고, PR이 오르는 걸 지켜봐요. 혼자여도 충분해요.",
            "start_note": True,
            "start": [
                ("스페이스 만들기", "홈에서 **새 스페이스 만들기**를 누르고(스페이스가 이미 있으면 **내 스페이스** 옆 **+** 버튼부터) **혼자 사용**을 골라요. 이름과 세션(운동 종류, 예: Running, Hyrox)만 정하면 4단계로 끝나요."),
                ("첫 운동 올리기", "세션을 열고 **+** 버튼을 눌러 오늘 할 운동을 적어요. 기록 방식(For Time, AMRAP, 스트렝스 등)을 하나 고르고 저장해요."),
                ("첫 기록 남기기", "운동을 열고 **내 점수 추가**로 결과와 메모를 남겨요. 스트렝스 운동은 세트마다 무게를 따로 적을 수 있어요."),
                ("첫 PR 기록하기", "**계정 → PR**에서 **+** 버튼을 눌러 1RM 같은 최고 기록을 남겨요. 기록이 쌓이면 차트로 성장이 보여요."),
                ("Showup 쌓기", "운동을 기록하면 그날이 홈의 Showup 카드에 쌓여요. 이번 달 운동한 날과 현재 Streak을 한눈에 봐요."),
            ],
            "more": [
                ("PR 대비 %로 내 무게 보기", "\"백스쿼트 1RM의 80%\"처럼 퍼센트로 짠 운동이라면, 운동 내용을 쓸 때 **PR 대비 %** 버튼을 눌러 넣어요. 내 PR로 계산된 무게가 바로 보여요."),
                ("친구와 함께", "같이 기록할 친구가 생기면 **커뮤니티 → 멤버**의 QR 코드로 불러와요. 자세한 방법은 [소규모 그룹 페이지](group-ko.html)에 있어요."),
            ],
            "note": None,
        },
        "group": {
            "title": "단톡방 대신, 우리 크루의 운동 공간",
            "subtitle": "운동을 올리면 멤버에게 알림이 가고, 기록마다 서로 응원해요.",
            "start_note": False,
            "start": [
                ("스페이스 만들기", "홈에서 **새 스페이스 만들기**(스페이스가 이미 있으면 **내 스페이스** 옆 **+** 버튼부터) → **소규모 그룹**을 골라요. 이름과 세션(예: Running, HIIT)을 정해요. 예약은 **아니오**, 멤버십 플랜은 **나중에 할게요**를 누르면 넘어가요."),
                ("첫 운동 올리기", "이번 모임에서 할 운동을 올려요. 멤버가 들어오면 운동을 올릴 때마다 알림이 가요."),
                ("멤버 데려오기", "**커뮤니티 → 멤버**에서 QR 코드를 보여 주거나, **복사하기**로 가입 링크를 단톡방에 올려요. 이메일이나 @사용자 이름으로 **멤버 초대**도 돼요. 가입 요청이 오면 **가입 요청 수락**만 누르면 돼요."),
                ("첫 기록 남기기", "운동을 마치면 **내 점수 추가**로 기록해요. 리더보드에서 서로의 기록을 보고 반응과 댓글로 응원해요."),
                ("커뮤니티에 첫 글 올리기", "환영 인사나 공지사항, 오늘 운동 인증을 올려요. 새 글도 멤버에게 알림이 가요."),
            ],
            "more": [
                ("PR 보드", "멤버가 남긴 PR이 커뮤니티 맨 위 PR 보드에 모여요. 종목마다 누가 앞서는지 한눈에 봐요."),
                ("콜라보 워크아웃", "다른 크루와 같은 운동을 하고, 리더보드 하나에서 함께 순위를 봐요."),
            ],
            "note": "무료 요금제로 스페이스마다 멤버 5명까지 함께할 수 있어요. 더 많은 인원은 [요금제](../pricing-ko.html)를 확인하세요.",
        },
        "gym": {
            "title": "WOD 공지부터 수업 예약,\n멤버십까지 한 앱에서",
            "subtitle": "화이트보드, 예약표, 회원 명단을 따로 챙기지 않아도 돼요.",
            "start_note": False,
            "start": [
                ("스페이스 만들기", "홈에서 **새 스페이스 만들기**(스페이스가 이미 있으면 **내 스페이스** 옆 **+** 버튼부터) → **체육관 또는 박스**를 골라요. 세션(WOD, Strength, Open Gym 등)을 고르고, 예약을 쓸지와 멤버십 플랜까지 정해요."),
                ("코치·스태프 초대하기", "**커뮤니티 → 멤버 → 멤버 초대**로 코치와 스태프를 초대해요. 코치는 운동을 올리고 수업을 진행하고, 스태프는 멤버와 설정까지 관리해요."),
                ("WOD 미리 올리기", "내일 WOD를 오늘 올리고 **운동 공개 예약**에서 공개 시간을 정해요. 그 시간에 멤버에게 공개되고 알림이 가요. 코치와 스태프는 미리 볼 수 있어요."),
                ("수업 일정 만들기", "스페이스의 **⋯** 메뉴에서 **일정 추가**를 눌러 수업 시간, 정원, 담당 코치를 정해요. 매주 반복도 돼요. 멤버는 **예약** 탭에서 자리를 잡고, 다 차면 대기자 명단에 올라가요."),
                ("회원 들이기", "스페이스 QR을 **사진에 저장**해 카운터에 붙여 두면, 회원이 찍고 가입을 요청해요. **가입 요청 수락** 후 **멤버 관리**에서 멤버십 플랜을 배정해요."),
            ],
            "more": [
                ("PR 대비 %", "WOD에 \"백스쿼트 80%\"를 넣으면 회원마다 자기 PR로 계산된 무게가 보여요. 박스만의 운동은 **스페이스 설정 → 스페이스 운동**에 등록해요."),
                ("멤버십 플랜과 홀딩", "플랜마다 기간, 크레딧(주 단위·월 단위·정액권·무제한), 취소 정책, 홀딩을 정해요. 재등록은 **멤버 관리**의 **기간 추가**로 해요."),
                ("리더보드와 커뮤니티", "매일 WOD 리더보드와 공지로 박스 분위기를 만들어요."),
                ("콜라보 워크아웃", "다른 박스와 같은 WOD로 친선전을 열고 리더보드 하나로 겨루어요."),
            ],
            "note": "예약과 멤버십 관리는 무료 요금제에서도 똑같이 동작해요. 무료 요금제는 스페이스마다 멤버 5명, 세션 2개까지예요. 회원이 늘면 [요금제](../pricing-ko.html)를 확인하세요. 유료 플랜은 3개월 무료 체험이 있어요.",
        },
        "program": {
            "title": "내 프로그램을 매일 아침, 회원 손에",
            "subtitle": "몇 주치를 미리 올려 두면 정한 시간에 공개되고, 회원마다 자기 무게로 보여요.",
            "start_note": False,
            "start": [
                ("스페이스 만들기", "홈에서 **새 스페이스 만들기**(스페이스가 이미 있으면 **내 스페이스** 옆 **+** 버튼부터) → **트레이닝 프로그램**을 골라요. Strength, Olympic Lifting, Run Club처럼 프로그램의 큰 줄기를 세션으로 정해요."),
                ("몇 주치 미리 올리기", "운동을 올릴 때 **운동 공개 예약**에서 공개 시간을 정해 두면, 그 시간에 하나씩 공개되고 회원에게 알림이 가요. 공개 전에는 회원에게 보이지 않아요."),
                ("PR 대비 %로 쓰기", "운동 내용을 쓸 때 **PR 대비 %** 버튼을 눌러 \"백스쿼트 1RM의 80%\"처럼 넣어요. 회원마다 자기 PR로 계산된 무게가 보여요. 프로그램만의 운동은 **스페이스 운동**에 등록해요."),
                ("회원 데려오기", "QR 코드나 가입 링크, 이메일 초대로 회원을 받아요. 멤버십 플랜에 기간을 정해 두면 누가 언제까지 회원인지 한눈에 보여요."),
                ("기록 보고 피드백하기", "회원이 남긴 점수와 메모를 리더보드에서 보고, 댓글로 피드백해요."),
            ],
            "more": [
                ("콜라보로 여러 스페이스에 배포", "같은 운동을 여러 박스·그룹과 공유하고, 리더보드 하나로 모아요. 콜라보 운동의 % 계산에는 Showup 운동만 쓸 수 있어요."),
                ("미디어 라이브러리", "동작 시범 영상을 한 번 저장해 두고 여러 운동에 붙여요. 유료 요금제에서 쓸 수 있어요."),
            ],
            "note": "무료 요금제는 스페이스마다 세션 2개, 멤버 5명까지예요. 프로그램이 커지면 [요금제](../pricing-ko.html)를 확인하세요. 유료 플랜은 3개월 무료 체험이 있어요.",
        },
        "member": {
            "title": "오늘 운동 확인부터 기록, 예약까지",
            "subtitle": "코치가 올린 운동을 보고, 기록하고, 함께 운동하는 사람들과 응원을 주고받아요.",
            "start_note": True,
            "start": [
                ("스페이스 들어가기", "홈에서 **스페이스 들어가기**를 눌러 코치에게 받은 QR을 비춰요(이미 스페이스가 있으면 **내 스페이스** 옆 **+** 버튼부터). 휴대폰 카메라로 찍어도 돼요. **가입** → **보내기**로 요청하면, 수락되는 대로 알림이 와요. 이메일로 초대받았다면 홈에서 초대를 수락하면 돼요."),
                ("오늘 운동 보고 기록 남기기", "스페이스에서 오늘 운동을 열고 **내 점수 추가**로 결과를 남겨요. Rx와 스케일드 중에서 고를 수도 있어요."),
                ("첫 PR 기록하기", "**계정 → PR**에서 1RM 같은 최고 기록을 남겨요. PR을 남겨 두면 코치가 \"백스쿼트 80%\"처럼 올린 운동에 내 무게가 바로 보여요."),
                ("수업 예약하기", "스페이스가 예약을 쓰면 **예약** 탭에서 수업을 고르고 **예약하기**를 눌러요. 자리가 다 찼으면 대기자 명단에 올라가고, 자리가 나면 자동으로 확정돼요."),
            ],
            "more": [
                ("리더보드에서 응원하기", "다른 멤버의 기록에 반응과 댓글을 남겨요."),
                ("내 멤버십", "**계정 → 내 멤버십**에서 남은 기간과 크레딧을 확인해요. 플랜이 허용하면 여행이나 부상 때 홀딩도 직접 걸 수 있어요."),
                ("알림 고르기", "새 운동, 공지, 예약 확정 알림을 **계정 → 알림**에서 골라 받아요."),
                ("커뮤니티", "오늘 운동 인증이나 소식을 올려요."),
            ],
            "note": None,
        },
    },
    # ------------------------------------------------------------------ en
    "en": {
        "solo": {
            "title": "Your own training log, now in Showup",
            "subtitle": "Post your workouts, log them and watch your PRs go up. It works just as well on your own.",
            "start_note": True,
            "start": [
                ("Create a space", "On the Home tab, tap **Create a new space** (if you already have a space, tap the **+** at the end of the **My Spaces** header first) and choose **Just for me**. Give it a name and pick your sessions (the kinds of training you do, like Running or Hyrox), and you're done in four steps."),
                ("Post your first workout", "Open a session and tap the **+** button to write down today's workout. Choose how it's scored (For Time, AMRAP, Strength and more) and save."),
                ("Log your first score", "Open the workout, tap **Add My Score** and enter your result and any notes. On a Strength workout you can log a weight for every set."),
                ("Log your first PR", "Go to **Account → Personal Records** and tap the **+** button to add a best, like your 1RM. As your records add up, a chart shows how far you've come."),
                ("Build your Showup", "Every day you log a workout is added to the Showup card on Home. See this month's training days and your Current Streak at a glance."),
            ],
            "more": [
                ("See your weights with % of PR", "If your program is written in percentages, like \"80% of your Back Squat 1RM\", tap the **% of PR** button while writing the workout. The weight worked out from your own PR shows up right away."),
                ("Train with friends", "When a friend wants to log with you, bring them in with the QR code in **Community → Members**. The [Small group page](group.html) shows how."),
            ],
            "note": None,
        },
        "group": {
            "title": "A training space for your crew, not just another group chat",
            "subtitle": "Post a workout and everyone gets a notification. Cheer each other on with every score.",
            "start_note": False,
            "start": [
                ("Create a space", "On the Home tab, tap **Create a new space** (if you already have a space, tap the **+** at the end of the **My Spaces** header first) and choose **Small group**. Give it a name and pick your sessions, like Running or HIIT. Tap **No** for booking and **Do it later** for membership plans to skip them."),
                ("Post your first workout", "Post what the group is doing next. Once members join, they get a notification every time you post a workout."),
                ("Bring in members", "In **Community → Members**, show your QR code, or tap **Copy** and drop the join link into your group chat. You can also use **Invite Member** to invite people by email or @username. When a join request comes in, just tap **Accept Request**."),
                ("Log your first score", "After the workout, log it with **Add My Score**. Check each other's scores on the leaderboard and cheer with reactions and comments."),
                ("Write your first community post", "Post a welcome, an announcement or a photo of today's workout. Members get a notification for new posts too."),
            ],
            "more": [
                ("PR Board", "Members' PRs come together on the PR Board at the top of Community. See who leads each lift at a glance."),
                ("Collaborative workouts", "Do the same workout as another crew and rank together on one leaderboard."),
            ],
            "note": "On the free plan, up to 5 members can join each space. For a bigger group, see [Pricing](../pricing.html).",
        },
        "gym": {
            "title": "From the WOD to class bookings and memberships, all in one app",
            "subtitle": "No more juggling a whiteboard, a booking sheet and a member list.",
            "start_note": False,
            "start": [
                ("Create a space", "On the Home tab, tap **Create a new space** (if you already have a space, tap the **+** at the end of the **My Spaces** header first) and choose **Gym or Box**. Pick your sessions (WOD, Strength, Open Gym and more), then decide on booking and membership plans."),
                ("Invite your coaches and staff", "Go to **Community → Members → Invite Member** to bring in your coaches and staff. Coaches post workouts and run classes, and staff also look after members and settings."),
                ("Post the WOD ahead", "Post tomorrow's WOD today and set when it goes live under **Schedule workout**. Members see it, and get a notification, at that time. Coaches and staff can see it early."),
                ("Create a class schedule", "From your space's **⋯** menu, tap **Add Schedule** and set the class time, capacity and coach. Classes can repeat every week. Members grab a spot in the **Booking** tab, and when a class is full they join the waitlist."),
                ("Bring in members", "Save your space's QR code with **Save to Photos** and put it up at the front desk. Members scan it to ask to join. Tap **Accept Request**, then assign a membership plan in **Manage Member**."),
            ],
            "more": [
                ("% of PR", "Write \"80% Back Squat\" in the WOD, and every member sees their own weight, worked out from their PR. Add your box's own movements under **Space Settings → Space Exercises**."),
                ("Membership plans and holds", "Set each plan's duration, credits (per week, per month, fixed pack or unlimited), cancellation policy and holds. To renew a member, use **Add period** in **Manage Member**."),
                ("Leaderboards and community", "Build your box's energy with a daily WOD leaderboard and announcements."),
                ("Collaborative workouts", "Run a friendly competition with another box: the same WOD, one shared leaderboard."),
            ],
            "note": "Booking and memberships work the same on the free plan. The free plan covers up to 5 members and 2 sessions per space. As you grow, see [Pricing](../pricing.html). Paid plans come with a 3-month free trial.",
        },
        "program": {
            "title": "Your program, in your members' hands every morning",
            "subtitle": "Post weeks ahead and release each workout on schedule, with every member seeing their own weights.",
            "start_note": False,
            "start": [
                ("Create a space", "On the Home tab, tap **Create a new space** (if you already have a space, tap the **+** at the end of the **My Spaces** header first) and choose **Training program**. Set up the main tracks of your program as sessions, like Strength, Olympic Lifting or Run Club."),
                ("Post weeks ahead", "When you post a workout, set a time under **Schedule workout**. Each workout goes live, and members get a notification, at its time. Until then, members can't see it."),
                ("Write with % of PR", "While writing a workout, tap the **% of PR** button to add something like \"80% of Back Squat 1RM\". Every member sees the weight worked out from their own PR. Add your program's own movements as **Space Exercises**."),
                ("Bring in members", "Take members in with a QR code, a join link or an email invitation. Give your membership plans a duration, and you'll see at a glance who's a member and until when."),
                ("Review scores and give feedback", "See your members' scores and notes on the leaderboard, and reply with comments."),
            ],
            "more": [
                ("Share across spaces with collaborative workouts", "Share the same workout with several boxes and groups, and bring everyone onto one leaderboard. In a collaborative workout, % of PR works with Showup Exercises only."),
                ("Media Library", "Save a movement demo once and attach it to as many workouts as you like. Available on paid plans."),
            ],
            "note": "The free plan covers 2 sessions and 5 members per space. As your program grows, see [Pricing](../pricing.html). Paid plans come with a 3-month free trial.",
        },
        "member": {
            "title": "From today's workout to logging it and booking your next class",
            "subtitle": "See what your coach posted, log it, and cheer on the people you train with.",
            "start_note": True,
            "start": [
                ("Join a space", "On the Home tab, tap **Join a space** and point the camera at the QR code your coach gave you (if you already have a space, tap the **+** at the end of the **My Spaces** header first). Your phone's camera app works too. Tap **Join**, then **Send** to ask, and you'll get a notification once you're accepted. Invited by email? Just accept the invitation on Home."),
                ("See today's workout and log it", "Open today's workout in your space and tap **Add My Score** to log your result. You can choose Rx or Scaled too."),
                ("Log your first PR", "Add a best, like your 1RM, in **Account → Personal Records**. Once it's in, workouts your coach writes like \"80% Back Squat\" show your own weight."),
                ("Book a class", "If your space uses booking, pick a class in the **Booking** tab and tap **Book**. If it's full, you join the waitlist and get the spot automatically when one opens up."),
            ],
            "more": [
                ("Cheer on the leaderboard", "React to and comment on other members' scores."),
                ("My Membership", "See how long your membership runs and how many credits you have left in **Account → My Memberships**. If your plan allows it, you can put it on hold yourself when you travel or get injured."),
                ("Choose your notifications", "Pick which notifications you get, like new workouts, announcements and booking confirmations, in **Account → Notifications**."),
                ("Community", "Post today's workout or share your news."),
            ],
            "note": None,
        },
    },
    # ------------------------------------------------------------------ de
    "de": {
        "solo": {
            "title": "Dein eigenes Trainingstagebuch – jetzt in Showup",
            "subtitle": "Poste deine Workouts, trag sie ein und sieh zu, wie deine PRs steigen. Auch allein funktioniert das bestens.",
            "start_note": True,
            "start": [
                ("Einen Space erstellen", "Tippe im Tab Start auf **Neuen Space erstellen** (hast du schon einen Space, tippe zuerst auf das **+** am Ende der Überschrift **Meine Spaces**) und wähle **Nur für mich**. Gib ihm einen Namen und wähle deine Sessions, also deine Trainingsarten wie Running oder Hyrox – nach vier Schritten bist du fertig."),
                ("Erstes Workout posten", "Öffne eine Session und tippe auf die Schaltfläche **+**, um das heutige Workout aufzuschreiben. Wähl aus, wie es gewertet wird (For Time, AMRAP, Kraft und mehr), und speichere."),
                ("Erstes Ergebnis eintragen", "Öffne das Workout, tippe auf **Mein Ergebnis hinzufügen** und trag dein Ergebnis und Notizen ein. Bei einem Kraft-Workout kannst du für jeden Satz ein Gewicht eintragen."),
                ("Ersten PR eintragen", "Geh zu **Konto → Persönliche Rekorde** und tippe auf **+**, um eine Bestleistung wie dein 1RM einzutragen. Je mehr Rekorde du sammelst, desto deutlicher zeigt dir ein Diagramm deinen Fortschritt."),
                ("Dein Showup aufbauen", "Jeder Tag, an dem du ein Workout einträgst, zählt auf der Showup-Karte im Tab Start. Sieh deine Trainingstage in diesem Monat und deine aktuelle Streak auf einen Blick."),
            ],
            "more": [
                ("Dein Gewicht mit % vom PR", "Ist dein Programm in Prozent geschrieben, etwa „80 % deines Back-Squat-1RM“, tippe beim Schreiben des Workouts auf die Schaltfläche **% vom PR**. Dein Gewicht, berechnet aus deinem eigenen PR, erscheint sofort."),
                ("Mit Freunden trainieren", "Will jemand mit dir zusammen eintragen, hol ihn mit dem QR-Code unter **Community → Mitglieder** dazu. Wie das geht, zeigt die Seite [„Kleine Gruppe“](group-de.html)."),
            ],
            "note": None,
        },
        "group": {
            "title": "Ein Trainingsraum für deine Crew – mehr als ein Gruppenchat",
            "subtitle": "Poste ein Workout, und alle werden benachrichtigt. Feuert euch bei jedem Ergebnis gegenseitig an.",
            "start_note": False,
            "start": [
                ("Einen Space erstellen", "Tippe im Tab Start auf **Neuen Space erstellen** (hast du schon einen Space, tippe zuerst auf das **+** am Ende der Überschrift **Meine Spaces**) und wähle **Kleine Gruppe**. Gib ihm einen Namen und wähle deine Sessions, etwa Running oder HIIT. Bei der Buchung tippst du auf **Nein**, bei den Mitgliedschaftsplänen auf **Später erledigen** – so überspringst du beides."),
                ("Erstes Workout posten", "Poste, was die Gruppe als Nächstes macht. Sobald Mitglieder dabei sind, werden sie bei jedem neuen Workout benachrichtigt."),
                ("Mitglieder dazuholen", "Zeig unter **Community → Mitglieder** euren QR-Code, oder tippe auf **Kopieren** und schick den Beitritts-Link in euren Gruppenchat. Mit **Mitglied einladen** kannst du Leute auch per E-Mail oder @Benutzername einladen. Kommt eine Beitrittsanfrage, tippst du einfach auf **Anfrage annehmen**."),
                ("Erstes Ergebnis eintragen", "Trag das Workout danach mit **Mein Ergebnis hinzufügen** ein. Schaut euch in der Rangliste gegenseitig die Ergebnisse an und feuert euch mit Reaktionen und Kommentaren an."),
                ("Ersten Community-Beitrag schreiben", "Poste eine Begrüßung, eine Ankündigung oder ein Foto vom heutigen Workout. Auch bei neuen Beiträgen werden die Mitglieder benachrichtigt."),
            ],
            "more": [
                ("PR-Tafel", "Die PRs der Mitglieder landen auf der PR-Tafel oben in der Community. So siehst du auf einen Blick, wer bei welcher Übung vorn liegt."),
                ("Kollaborative Workouts", "Macht dasselbe Workout wie eine andere Crew und vergleicht euch in einer gemeinsamen Rangliste."),
            ],
            "note": "Im Gratistarif können pro Space bis zu 5 Mitglieder dabei sein. Für größere Gruppen sieh dir die [Preise](../pricing-de.html) an.",
        },
        "gym": {
            "title": "Vom WOD über Kursbuchungen bis zur Mitgliedschaft – alles in einer App",
            "subtitle": "Kein Jonglieren mehr mit Whiteboard, Buchungsliste und Mitgliederliste.",
            "start_note": False,
            "start": [
                ("Einen Space erstellen", "Tippe im Tab Start auf **Neuen Space erstellen** (hast du schon einen Space, tippe zuerst auf das **+** am Ende der Überschrift **Meine Spaces**) und wähle **Gym oder Box**. Wähle deine Sessions (WOD, Strength, Open Gym und mehr) und entscheide dann über Buchung und Mitgliedschaftspläne."),
                ("Coaches und Staff einladen", "Hol deine Coaches und dein Staff über **Community → Mitglieder → Mitglied einladen** dazu. Coaches posten Workouts und leiten Kurse, das Staff kümmert sich zusätzlich um Mitglieder und Einstellungen."),
                ("Das WOD im Voraus posten", "Poste das WOD von morgen schon heute und leg unter **Workout planen** fest, wann es sichtbar wird. Dann sehen es die Mitglieder und werden benachrichtigt. Coaches und Staff sehen es schon vorher."),
                ("Kurstermine anlegen", "Tippe im Menü **⋯** deines Space auf **Termin hinzufügen** und leg Uhrzeit, Kapazität und Coach fest. Kurse können sich jede Woche wiederholen. Mitglieder sichern sich im Tab **Buchung** einen Platz, und ist ein Kurs voll, kommen sie auf die Warteliste."),
                ("Mitglieder aufnehmen", "Speichere den QR-Code deines Space mit **In Fotos speichern** und häng ihn am Empfang auf. Mitglieder scannen ihn und fragen den Beitritt an. Tippe auf **Anfrage annehmen** und weise dann unter **Mitglied verwalten** einen Mitgliedschaftsplan zu."),
            ],
            "more": [
                ("% vom PR", "Schreib „80 % Back Squat“ ins WOD, und jedes Mitglied sieht sein eigenes Gewicht, berechnet aus seinem PR. Eigene Übungen deiner Box legst du unter **Einstellungen → Space-Übungen** an."),
                ("Mitgliedschaftspläne und Pausen", "Leg für jeden Plan Laufzeit, Credits (pro Woche, pro Monat, festes Paket oder unbegrenzt), Stornierungsrichtlinie und Pausen fest. Verlängern kannst du eine Mitgliedschaft unter **Mitglied verwalten** mit **Zeitraum hinzufügen**."),
                ("Rangliste und Community", "Sorg mit einer täglichen WOD-Rangliste und Ankündigungen für Stimmung in deiner Box."),
                ("Kollaborative Workouts", "Veranstalte einen freundschaftlichen Wettkampf mit einer anderen Box: dasselbe WOD, eine gemeinsame Rangliste."),
            ],
            "note": "Buchung und Mitgliedschaften funktionieren im Gratistarif genauso. Der Gratistarif umfasst pro Space bis zu 5 Mitglieder und 2 Sessions. Wenn du wächst, sieh dir die [Preise](../pricing-de.html) an. Bezahlte Tarife kannst du 3 Monate gratis testen.",
        },
        "program": {
            "title": "Dein Programm – jeden Morgen bei deinen Mitgliedern",
            "subtitle": "Poste Wochen im Voraus und gib jedes Workout zur geplanten Zeit frei – jedes Mitglied sieht dabei seine eigenen Gewichte.",
            "start_note": False,
            "start": [
                ("Einen Space erstellen", "Tippe im Tab Start auf **Neuen Space erstellen** (hast du schon einen Space, tippe zuerst auf das **+** am Ende der Überschrift **Meine Spaces**) und wähle **Trainingsprogramm**. Leg die Hauptstränge deines Programms als Sessions an, etwa Strength, Olympic Lifting oder Run Club."),
                ("Wochen im Voraus posten", "Leg beim Posten eines Workouts unter **Workout planen** eine Zeit fest. Jedes Workout wird zu seiner Zeit sichtbar, und die Mitglieder werden benachrichtigt. Vorher sehen sie es nicht."),
                ("Mit % vom PR schreiben", "Tippe beim Schreiben eines Workouts auf die Schaltfläche **% vom PR**, um etwa „80 % vom Back-Squat-1RM“ einzufügen. Jedes Mitglied sieht das Gewicht, berechnet aus seinem eigenen PR. Eigene Übungen deines Programms legst du als **Space-Übungen** an."),
                ("Mitglieder dazuholen", "Nimm Mitglieder per QR-Code, Beitritts-Link oder E-Mail-Einladung auf. Gib deinen Mitgliedschaftsplänen eine Laufzeit, dann siehst du auf einen Blick, wer bis wann dabei ist."),
                ("Ergebnisse ansehen und Feedback geben", "Sieh dir die Ergebnisse und Notizen deiner Mitglieder in der Rangliste an und antworte mit Kommentaren."),
            ],
            "more": [
                ("Mit kollaborativen Workouts über Spaces hinweg teilen", "Teile dasselbe Workout mit mehreren Boxen und Gruppen und bring alle in eine gemeinsame Rangliste. In kollaborativen Workouts funktioniert % vom PR nur mit Showup-Übungen."),
                ("Medienbibliothek", "Speichere ein Übungsvideo einmal und häng es an beliebig viele Workouts. In bezahlten Tarifen verfügbar."),
            ],
            "note": "Der Gratistarif umfasst pro Space 2 Sessions und 5 Mitglieder. Wächst dein Programm, sieh dir die [Preise](../pricing-de.html) an. Bezahlte Tarife kannst du 3 Monate gratis testen.",
        },
        "member": {
            "title": "Vom heutigen Workout übers Eintragen bis zur Kursbuchung",
            "subtitle": "Sieh, was dein Coach gepostet hat, trag es ein und feuere die an, mit denen du trainierst.",
            "start_note": True,
            "start": [
                ("Space beitreten", "Tippe im Tab Start auf **Space beitreten** und richte die Kamera auf den QR-Code von deinem Coach (hast du schon einen Space, tippe zuerst auf das **+** am Ende der Überschrift **Meine Spaces**). Die Kamera-App deines Handys geht auch. Tippe auf **Beitreten** und dann auf **Senden**, um anzufragen – sobald du angenommen bist, bekommst du eine Benachrichtigung. Per E-Mail eingeladen? Nimm die Einladung einfach im Tab Start an."),
                ("Heutiges Workout ansehen und eintragen", "Öffne das heutige Workout in deinem Space und tippe auf **Mein Ergebnis hinzufügen**. Du kannst dabei auch Rx oder Scaled wählen."),
                ("Ersten PR eintragen", "Trag unter **Konto → Persönliche Rekorde** eine Bestleistung wie dein 1RM ein. Danach zeigen Workouts, in die dein Coach etwa „80 % Back Squat“ schreibt, dein eigenes Gewicht."),
                ("Kurs buchen", "Nutzt dein Space die Buchung, wähl im Tab **Buchung** einen Kurs und tippe auf **Buchen**. Ist er voll, kommst du auf die Warteliste und bekommst den Platz automatisch, sobald einer frei wird."),
            ],
            "more": [
                ("In der Rangliste anfeuern", "Reagiere auf die Ergebnisse anderer Mitglieder und kommentiere sie."),
                ("Meine Mitgliedschaft", "Sieh unter **Konto → Meine Mitgliedschaften**, wie lange deine Mitgliedschaft läuft und wie viele Credits du noch hast. Erlaubt es dein Plan, kannst du sie bei Urlaub oder Verletzung selbst pausieren."),
                ("Benachrichtigungen wählen", "Leg unter **Konto → Benachrichtigungen** fest, worüber du benachrichtigt wirst, etwa neue Workouts, Ankündigungen und Buchungsbestätigungen."),
                ("Community", "Poste dein heutiges Workout oder teile Neuigkeiten."),
            ],
            "note": None,
        },
    },
}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def inline(text, link=None):
    """Escape text, then turn **x** into <strong> and [text](url) into links.

    Links are written as seen from start/<page>.html; `link(url)` may return the
    (href, data-target) to use instead, for the Help Center copy.
    """
    out, i = [], 0
    while i < len(text):
        if text.startswith("**", i):
            j = text.index("**", i + 2)
            out.append("<strong>" + html.escape(text[i + 2:j], quote=False) + "</strong>")
            i = j + 2
        elif text[i] == "[" and "](" in text[i:]:
            j = text.index("](", i)
            k = text.index(")", j)
            label, url = text[i + 1:j], text[j + 2:k]
            href, target = link(url) if link else (url, None)
            attr = ' data-target="%s"' % target if target else ""
            out.append('<a%s href="%s">%s</a>' % (attr, html.escape(href), html.escape(label, quote=False)))
            i = k + 1
        else:
            j = i
            while j < len(text) and not text.startswith("**", j) and not (text[j] == "[" and "](" in text[j:]):
                j += 1
            out.append(html.escape(text[i:j], quote=False))
            i = j
    return "".join(out)


def phone(lang, shot):
    d = shot_dir(lang)
    alt = html.escape(ALT[shot][lang])
    return (
        '<figure class="phone">'
        f'<img class="shot-light" src="../assets/screenshots/{d}/{shot}.webp" alt="{alt}" width="1080" height="2347" loading="lazy" decoding="async">'
        f'<img class="shot-dark" src="../assets/screenshots/{d}/{shot}-dark.webp" alt="{alt}" width="1080" height="2347" loading="lazy" decoding="async">'
        "</figure>"
    )


def item(lang, kind, n, title, body, shots):
    marker = f'<span class="step-num" aria-hidden="true">{n}</span>' if kind == "start" else ""
    phones = ""
    if shots:
        phones = f'<div class="phones phones-{len(shots)}">' + "".join(phone(lang, s) for s in shots) + "</div>"
    cls = "step" + ("" if shots else " step-text")
    return (
        f'<li class="{cls}">'
        f'<div class="step-text-col">{marker}<h3>{inline(title)}</h3><p>{inline(body)}</p></div>'
        f"{phones}</li>"
    )


APPLE_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>')
PLAY_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M1.22 0.345C0.947 0.639 0.787 1.089 0.787 1.674V22.326c0 0.585 0.16 1.035 0.433 1.329l0.07 0.068L13.068 12V11.862L1.29 0.277 1.22 0.345z" fill="#4285F4"/><path d="M17 16.003l-3.932-3.934V11.931L17 7.997l0.088 0.05 4.66 2.647c1.33 0.756 1.33 1.993 0 2.749L17.088 16.09 17 16.003z" fill="#FFBC00"/><path d="M17.088 16.09L13.068 12 1.22 23.655c0.439 0.465 1.162 0.522 1.982 0.058L17.088 16.09z" fill="#EA4335"/><path d="M17.088 7.91L3.202 0.287C2.382-0.177 1.659-0.12 1.22 0.345L13.068 12l4.02-4.09z" fill="#34A853"/></svg>')

SUN_SVG = '<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
MOON_SVG = '<svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'

CSS = """
        :root {
            --bg-primary: #0A0A0A;
            --bg-secondary: #111111;
            --text-primary: #FFFFFF;
            --text-secondary: rgba(255, 255, 255, 0.6);
            --text-tertiary: rgba(255, 255, 255, 0.35);
            --border: rgba(255, 255, 255, 0.2);
            --rule: rgba(255, 255, 255, 0.1);
            --bezel: #1A1A1A;
            --bezel-edge: rgba(255, 255, 255, 0.2);
            --screen: #000;
            --nav-height: 72px;
        }
        [data-theme="light"] {
            --bg-primary: #FFFFFF;
            --bg-secondary: #F5F5F7;
            --text-primary: #1A1A1A;
            --text-secondary: rgba(26, 26, 26, 0.6);
            --text-tertiary: rgba(26, 26, 26, 0.38);
            --border: rgba(0, 0, 0, 0.15);
            --rule: rgba(0, 0, 0, 0.08);
            --bezel: #E0E0E0;
            --bezel-edge: rgba(0, 0, 0, 0.15);
            --screen: #F5F5F5;
        }
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: var(--text-primary);
            background: var(--bg-primary);
            line-height: 1.6;
            overflow-x: clip;
        }
        a { color: inherit; text-decoration: none; }
        h1, h2, h3 {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            letter-spacing: -0.02em;
        }
        :lang(ko) h1, :lang(ko) h2, :lang(ko) h3 {
            font-family: 'Apple SD Gothic Neo', 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        }
        :lang(ko) body { word-break: keep-all; }

        /* Navigation (same as the other pages) */
        .nav { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; height: var(--nav-height); background: var(--bg-primary); border-bottom: 1px solid var(--rule); }
        .nav-inner { max-width: 1280px; margin: 0 auto; padding: 0 32px; height: 100%; display: flex; align-items: center; justify-content: space-between; position: relative; }
        .nav-logo { display: flex; align-items: center; position: absolute; left: 50%; transform: translateX(-50%); }
        .nav-logo img { height: 34px; width: auto; display: block; }
        img.logo-dark { display: block; }
        img.logo-light { display: none; }
        [data-theme="light"] img.logo-dark { display: none; }
        [data-theme="light"] img.logo-light { display: block; }
        .nav-actions { display: flex; align-items: center; gap: 8px; margin-left: auto; }
        .lang-dropdown { position: relative; flex-shrink: 0; }
        .lang-current { display: flex; align-items: center; gap: 4px; padding: 6px 4px; background: transparent; border: none; color: var(--text-secondary); font-family: inherit; font-weight: 600; font-size: 0.75rem; letter-spacing: 0.04em; text-transform: uppercase; cursor: pointer; transition: color 0.2s ease; }
        .lang-current:hover { color: var(--text-primary); }
        .lang-current svg { width: 10px; height: 10px; transition: transform 0.2s ease; }
        .lang-dropdown.open .lang-current svg { transform: rotate(180deg); }
        .lang-menu { position: absolute; top: calc(100% + 6px); right: 0; background: var(--bg-primary); border: 1px solid var(--border); min-width: 100%; opacity: 0; pointer-events: none; transform: translateY(-4px); transition: opacity 0.15s ease, transform 0.15s ease; z-index: 100; }
        .lang-dropdown.open .lang-menu { opacity: 1; pointer-events: auto; transform: translateY(0); }
        .lang-menu a { display: block; width: 100%; padding: 8px 12px; color: var(--text-secondary); font-weight: 600; font-size: 0.75rem; letter-spacing: 0.04em; text-transform: uppercase; transition: color 0.15s ease, background 0.15s ease; }
        .lang-menu a:hover { color: var(--text-primary); background: rgba(255,255,255,0.06); }
        [data-theme="light"] .lang-menu a:hover { background: rgba(0,0,0,0.04); }
        .lang-menu a.active { color: var(--text-primary); }
        .theme-toggle { width: 38px; height: 38px; border: none; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: transparent; cursor: pointer; transition: color 0.3s ease; color: var(--text-secondary); }
        .theme-toggle:hover { color: var(--text-primary); }
        .theme-toggle svg { width: 18px; height: 18px; }
        .icon-sun { display: block; }
        .icon-moon { display: none; }
        [data-theme="light"] .icon-sun { display: none; }
        [data-theme="light"] .icon-moon { display: block; }

        /* Page */
        .start { max-width: 1040px; margin: 0 auto; padding: calc(var(--nav-height) + 64px) 32px 96px; }
        .start-eyebrow { display: inline-block; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-secondary); padding-bottom: 6px; border-bottom: 1px solid var(--text-tertiary); margin-bottom: 28px; }
        .start-head h1 { font-weight: 900; font-size: clamp(2rem, 4.6vw, 3.4rem); line-height: 1.12; letter-spacing: -0.035em; max-width: 860px; }
        :lang(ko) .start-head h1 { line-height: 1.25; }
        .start-head p { margin-top: 20px; max-width: 640px; color: var(--text-secondary); font-size: 1.12rem; line-height: 1.7; }

        .start-section { margin-top: 88px; }
        .start-section > h2 { font-weight: 900; font-size: clamp(1.5rem, 2.6vw, 2rem); line-height: 1.2; padding-bottom: 18px; border-bottom: 1px solid var(--border); }
        .start-note { margin-top: 14px; color: var(--text-tertiary); font-size: 0.92rem; }
        .start-note strong { color: var(--text-secondary); font-weight: 600; }

        .steps { list-style: none; }
        .step { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 48px; align-items: center; padding: 48px 0; border-bottom: 1px solid var(--rule); }
        .step.step-text { grid-template-columns: minmax(0, 1fr); padding: 36px 0; }
        .step-text-col { max-width: 440px; }
        .step-num { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 50%; border: 1px solid var(--border); font-size: 0.85rem; font-weight: 700; color: var(--text-primary); margin-bottom: 18px; }
        .step h3 { font-weight: 800; font-size: 1.35rem; line-height: 1.3; margin-bottom: 12px; }
        .step p { color: var(--text-secondary); font-size: 1rem; line-height: 1.8; }
        .step p strong { color: var(--text-primary); font-weight: 600; }
        .step p a, .start-bottom-note a { color: var(--text-primary); text-decoration: underline; text-underline-offset: 3px; }
        .step p a:hover, .start-bottom-note a:hover { opacity: 0.7; }

        .phones { display: flex; gap: 20px; justify-content: flex-end; }
        .phone { width: 210px; aspect-ratio: 1080 / 2347; flex-shrink: 0; padding: 5px; border-radius: 36px; background: var(--bezel); border: 1.5px solid var(--bezel-edge); }
        .phone img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: top; border-radius: 30px; background: var(--screen); }
        .phone .shot-light { display: none; }
        [data-theme="light"] .phone .shot-light { display: block; }
        [data-theme="light"] .phone .shot-dark { display: none; }
        .phones-3 .phone { width: 180px; border-radius: 32px; }
        .phones-3 .phone img { border-radius: 26px; }

        .start-bottom { margin-top: 88px; }
        .start-bottom-note { color: var(--text-secondary); font-size: 0.98rem; line-height: 1.8; max-width: 640px; margin-bottom: 40px; }
        .start-cta { border: 1px solid var(--border); padding: 36px 32px; display: flex; align-items: center; justify-content: space-between; gap: 24px; flex-wrap: wrap; }
        .start-cta h2 { font-weight: 900; font-size: 1.5rem; }
        .start-stores { display: flex; gap: 12px; flex-wrap: wrap; }
        .btn { display: inline-flex; align-items: center; gap: 10px; padding: 12px 24px; border-radius: 100px; font-weight: 800; font-size: 0.88rem; text-transform: uppercase; border: 2px solid transparent; white-space: nowrap; transition: opacity 0.15s ease; }
        .btn:hover { opacity: 0.85; }
        .btn svg { width: 20px; height: 20px; }
        .btn-store { background: #fff; color: #0A0A0A; border-color: #fff; }
        [data-theme="light"] .btn-store { background: #1A1A1A; color: #F4F4F4; border-color: #1A1A1A; }

        .start-others { margin-top: 56px; }
        .start-others h2 { font-weight: 800; font-size: 1rem; color: var(--text-secondary); margin-bottom: 16px; letter-spacing: 0; }
        .start-others ul { list-style: none; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
        .start-others a { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 16px 18px; border: 1px solid var(--border); font-weight: 600; font-size: 0.95rem; transition: background 0.15s ease; }
        .start-others a:hover { background: var(--bg-secondary); }
        .start-others a::after { content: '→'; color: var(--text-tertiary); }

        @media (max-width: 900px) {
            .start-others ul { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 768px) {
            :root { --nav-height: 64px; }
            .nav-inner { padding: 0 16px; }
            .start { padding: calc(var(--nav-height) + 40px) 16px 72px; }
            .start-section { margin-top: 64px; }
            .step { grid-template-columns: minmax(0, 1fr); gap: 28px; padding: 36px 0; }
            .step-text-col { max-width: none; }
            /* Phones sit in a row that scrolls sideways when they don't fit. */
            .phones { justify-content: flex-start; overflow-x: auto; scroll-snap-type: x mandatory; margin: 0 -16px; padding: 0 16px 4px; scrollbar-width: none; }
            .phones::-webkit-scrollbar { display: none; }
            .phone, .phones-3 .phone { width: min(46vw, 210px); border-radius: 30px; scroll-snap-align: start; }
            .phone img, .phones-3 .phone img { border-radius: 25px; }
            .phones-1 .phone { width: min(58vw, 240px); }
            .start-cta { padding: 28px 20px; }
        }
        @media (max-width: 480px) {
            .nav-logo img { height: 28px; }
            .start-head h1 { font-size: 1.75rem; }
            .start-others ul { grid-template-columns: minmax(0, 1fr); }
            .start-stores, .start-stores .btn { width: 100%; justify-content: center; }
        }
        @media (prefers-reduced-motion: reduce) {
            * { transition-duration: 0.01ms !important; scroll-behavior: auto !important; }
        }
"""

SCRIPT = """
        (function () {
            var toggle = document.getElementById('themeToggle');
            var favicon = document.getElementById('favicon');
            function setTheme(theme) {
                document.documentElement.setAttribute('data-theme', theme);
                favicon.href = theme === 'light' ? '../assets/favicon-light.svg' : '../assets/favicon-dark.svg';
            }
            toggle.addEventListener('click', function () {
                var next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
                setTheme(next);
                localStorage.setItem('theme', next);
            });
            window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', function (e) {
                localStorage.removeItem('theme');
                setTheme(e.matches ? 'light' : 'dark');
            });

            var dropdown = document.getElementById('langDropdown');
            document.getElementById('langCurrent').addEventListener('click', function () {
                dropdown.classList.toggle('open');
            });
            document.addEventListener('click', function (e) {
                if (!dropdown.contains(e.target)) dropdown.classList.remove('open');
            });
        })();
"""


def build(lang, page):
    c = COMMON[lang]
    p = COPY[lang][page]
    steps = STEPS[page]
    name = NAMES[lang][page]
    if len(p["start"]) != len(steps["start"]) or len(p["more"]) != len(steps["more"]):
        sys.exit(f"{lang}/{page}: copy and STEPS have different lengths")

    title = html.escape(c["title"].format(name=name))
    desc = html.escape(p["subtitle"])
    # A "\n" in a page title is a deliberate line break.
    title_html = " <br>".join(html.escape(part) for part in p["title"].split("\n"))
    sfx = suffix(lang)
    self_url = f"{SITE}/start/{page}{sfx}.html"

    alternates = "\n".join(
        f'    <link rel="alternate" hreflang="{l}" href="{SITE}/start/{page}{suffix(l)}.html">' for l in LANGS
    ) + f'\n    <link rel="alternate" hreflang="x-default" href="{SITE}/start/{page}.html">'

    def lang_link(l):
        active = ' class="active"' if l == lang else ""
        return f'                        <a href="{page}{suffix(l)}.html"{active}>{COMMON[l]["lang_label"]}</a>'

    lang_links = "\n".join(lang_link(l) for l in ["en", "ko", "de"])

    start_items = "\n".join(
        "                " + item(lang, "start", i + 1, t, b, steps["start"][i]) for i, (t, b) in enumerate(p["start"])
    )
    more_items = "\n".join(
        "                " + item(lang, "more", i + 1, t, b, steps["more"][i]) for i, (t, b) in enumerate(p["more"])
    )
    note = f'\n            <p class="start-note">{inline(c["start_note"])}</p>' if p["start_note"] else ""
    bottom_note = f'\n            <p class="start-bottom-note">{inline(p["note"])}</p>' if p["note"] else ""

    others_title = c["others_member"] if page == "member" else c["others"]
    others = "\n".join(
        f'                <li><a href="{o}{sfx}.html">{html.escape(NAMES[lang][o])}</a></li>'
        for o in PAGE_ORDER if o != page
    )

    return f"""<!DOCTYPE html>
<!-- Generated by tools/build_start_pages.py — edit there, not here. -->
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{self_url}">
{alternates}
    <link rel="icon" id="favicon" type="image/svg+xml" href="../assets/favicon-dark.svg">
    <script>
        (function() {{
            var stored = localStorage.getItem('theme');
            var theme = stored || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
            document.documentElement.setAttribute('data-theme', theme);
            document.getElementById('favicon').href = theme === 'light' ? '../assets/favicon-light.svg' : '../assets/favicon-dark.svg';
        }})();
    </script>
    <link rel="stylesheet" href="../assets/css/footer.css">
    <style>{CSS}    </style>
</head>
<body>

    <nav class="nav">
        <div class="nav-inner">
            <a href="../index.html" class="nav-logo">
                <img src="../assets/images/logo-dark.svg" alt="showup" class="logo-dark">
                <img src="../assets/images/logo-light.svg" alt="showup" class="logo-light">
            </a>
            <div class="nav-actions">
                <div class="lang-dropdown" id="langDropdown">
                    <button class="lang-current" id="langCurrent" aria-label="Change language">
                        <span>{c["lang_label"]}</span>
                        <svg viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 1l4 4 4-4"/></svg>
                    </button>
                    <div class="lang-menu">
{lang_links}
                    </div>
                </div>
                <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                    {SUN_SVG}
                    {MOON_SVG}
                </button>
            </div>
        </div>
    </nav>

    <main class="start">
        <header class="start-head">
            <span class="start-eyebrow">{html.escape(name)}</span>
            <h1>{title_html}</h1>
            <p>{html.escape(p["subtitle"])}</p>
        </header>

        <section class="start-section" aria-labelledby="getting-started">
            <h2 id="getting-started">{html.escape(c["start"])}</h2>{note}
            <ol class="steps">
{start_items}
            </ol>
        </section>

        <section class="start-section" aria-labelledby="more">
            <h2 id="more">{html.escape(c["more"])}</h2>
            <ul class="steps">
{more_items}
            </ul>
        </section>

        <section class="start-bottom">{bottom_note}
            <div class="start-cta">
                <h2>{html.escape(c["open"])}</h2>
                <div class="start-stores">
                    <a href="{APP_STORE_URL}" target="_blank" rel="noopener" class="btn btn-store">{APPLE_SVG}<span>App Store</span></a>
                    <a href="{PLAY_STORE_URL}" target="_blank" rel="noopener" class="btn btn-store">{PLAY_SVG}<span>Google Play</span></a>
                </div>
            </div>
            <nav class="start-others" aria-labelledby="others">
                <h2 id="others">{html.escape(others_title)}</h2>
                <ul>
{others}
                </ul>
            </nav>
        </section>
    </main>

    <!-- footer:start — generated by tools/sync_footer.py, edit there not here -->
<!-- footer:end -->

    <script>{SCRIPT}    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Help Center: the same five guides as articles in help.html, -ko and -de, in
# their own sidebar group. Written between markers; the rest of each help page
# is hand-edited and left alone.
# ---------------------------------------------------------------------------
HELP_FILES = {"en": "help.html", "ko": "help-ko.html", "de": "help-de.html"}
HELP_GROUP = {"en": "Guides by use", "ko": "용도별 가이드", "de": "Leitfäden nach Nutzung"}
HELP_OTHERS = {"en": "The other guides", "ko": "다른 용도 가이드", "de": "Die anderen Leitfäden"}

# The banner at the top of the Welcome article: the same words as the welcome
# email's "How will you use Showup?" block and its five cards.
BANNER = {
    "ko": {
        "title": "Showup을 어떻게 쓰실 건가요?",
        "lead": "하나를 고르면 처음에 할 일을 화면과 함께 보여드릴게요.",
        "go": "가이드 보기",
        "cards": {
            "solo": "내 운동과 성장을 기록해요",
            "group": "친구나 동호회와 함께 운동해요",
            "gym": "회원을 코치하고 체육관을 운영해요",
            "program": "내 운동 프로그램을 회원과 나눠요",
            "member": "코치나 친구의 스페이스에서 시작해요",
        },
    },
    "en": {
        "title": "How will you use Showup?",
        "lead": "Pick one, and we'll show you what to do first, with screenshots.",
        "go": "View guide",
        "cards": {
            "solo": "Track your own workouts and progress",
            "group": "Work out with friends or a club",
            "gym": "Coach members and run your gym",
            "program": "Share your training program with members",
            "member": "Get started in your coach's or friend's space",
        },
    },
    "de": {
        "title": "Wie möchtest du Showup nutzen?",
        "lead": "Wähl eins aus, und wir zeigen dir mit Screenshots, womit du anfängst.",
        "go": "Leitfaden ansehen",
        "cards": {
            "solo": "Verfolge deine eigenen Workouts und Fortschritte",
            "group": "Trainiere mit Freunden oder einem Club",
            "gym": "Coache Mitglieder und führe dein Gym",
            "program": "Teile dein Trainingsprogramm mit deinen Mitgliedern",
            "member": "Starte im Space deines Coaches oder deiner Freunde",
        },
    },
}

NAV_START = "<!-- guides-nav:start — generated by tools/build_start_pages.py, edit there not here -->"
NAV_END = "<!-- guides-nav:end -->"
ART_START = "<!-- guides:start — generated by tools/build_start_pages.py, edit there not here -->"
ART_END = "<!-- guides:end -->"
BANNER_START = "<!-- guides-banner:start — generated by tools/build_start_pages.py, edit there not here -->"
BANNER_END = "<!-- guides-banner:end -->"
CSS_START = "/* guides:start — generated by tools/build_start_pages.py, edit there not here */"
CSS_END = "/* guides:end */"

HELP_CSS = """
        .help-article.guide h1 { text-transform: none; }
        .help-article .guide-eyebrow { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 10px; }
        .help-article .guide-lead { font-size: 1.05rem; }
        .help-article .guide-note { font-size: 0.9rem; color: var(--text-tertiary); }
        .guide { --bezel: #1A1A1A; --bezel-edge: rgba(255, 255, 255, 0.2); --screen: #000; }
        [data-theme="light"] .guide { --bezel: #E0E0E0; --bezel-edge: rgba(0, 0, 0, 0.15); --screen: #F5F5F5; }
        .guide-step { padding: 28px 0; border-top: 1px solid var(--border); }
        .help-article .guide-step h3 { display: flex; align-items: center; gap: 10px; font-size: 1.08rem; font-weight: 800; line-height: 1.35; margin-bottom: 8px; color: var(--text-primary); }
        .guide-num { flex-shrink: 0; width: 24px; height: 24px; border-radius: 50%; border: 1px solid var(--border); display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; }
        .help-article .guide-step p { margin-bottom: 0; }
        .guide-phones { display: flex; gap: 14px; margin-top: 18px; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
        .guide-phones::-webkit-scrollbar { display: none; }
        .guide-phone { width: 170px; flex-shrink: 0; aspect-ratio: 1080 / 2347; padding: 4px; border-radius: 30px; background: var(--bezel); border: 1.5px solid var(--bezel-edge); scroll-snap-align: start; margin: 0; }
        .guide-phone img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: top; border-radius: 25px; background: var(--screen); }
        .guide-phone .shot-light { display: none; }
        [data-theme="light"] .guide-phone .shot-light { display: block; }
        [data-theme="light"] .guide-phone .shot-dark { display: none; }
        .guides-banner { margin-bottom: 48px; padding: 36px 36px 32px; background: var(--bg-secondary); border: 1px solid var(--border); }
        [data-theme="light"] .guides-banner { background: #F5F5F7; }
        .help-article .guides-banner-eyebrow { margin-bottom: 10px; font-size: 0.75rem; font-weight: 700; line-height: 1.6; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-secondary); }
        .help-article .guides-banner h2 { margin: 0 0 10px; font-size: clamp(1.6rem, 3vw, 2.125rem); font-weight: 900; line-height: 1.2; letter-spacing: -0.035em; text-wrap: balance; }
        .help-article .guides-banner-lead { margin: 0; font-size: 1rem; line-height: 1.6; text-wrap: balance; }
        .guides-tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 26px; }
        .help-article a.guides-tile { display: flex; flex-direction: column; gap: 6px; min-height: 124px; padding: 18px 18px 16px; background: var(--bg-primary); border: 1px solid var(--border); color: var(--text-primary); text-decoration: none; word-break: keep-all; transition: border-color 0.15s ease; }
        [data-theme="light"] .help-article a.guides-tile { background: #FFFFFF; }
        .help-article a.guides-tile:hover { opacity: 1; border-color: var(--text-secondary); }
        .help-article a.guides-tile:focus-visible { outline: 2px solid var(--text-primary); outline-offset: 2px; }
        .guides-tile-name { font-size: 1rem; font-weight: 800; line-height: 1.35; }
        .guides-tile-desc { font-size: 0.85rem; line-height: 1.5; color: var(--text-secondary); }
        .guides-tile-go { margin-top: auto; padding-top: 4px; font-size: 0.8rem; font-weight: 700; }
        @media (max-width: 600px) {
            .guide-phone { width: min(42vw, 170px); }
            .guides-banner { margin-bottom: 40px; padding: 24px 20px; }
            .guides-tiles { grid-template-columns: 1fr; gap: 8px; margin-top: 20px; }
            .help-article a.guides-tile { display: grid; grid-template-columns: 1fr auto; column-gap: 12px; row-gap: 2px; align-items: center; min-height: 0; padding: 14px 16px; }
            .guides-tile-go { grid-column: 2; grid-row: 1 / span 2; margin: 0; padding: 0; font-size: 1rem; }
            .guides-tile-go-text { display: none; }
        }
"""


def help_link(lang):
    """Map a link written for start/<page>.html to the Help Center page at the site root."""
    def link(url):
        if url.startswith("../"):
            return url[3:], None
        page = url.split(".html")[0].split("-")[0]
        if page in PAGE_ORDER:
            return "#start-" + page, "start-" + page
        return url, None
    return link


def help_phone(lang, shot):
    d = shot_dir(lang)
    alt = html.escape(ALT[shot][lang])
    return (
        '<figure class="guide-phone">'
        f'<img class="shot-light" src="assets/screenshots/{d}/{shot}.webp" alt="{alt}" width="1080" height="2347" loading="lazy" decoding="async">'
        f'<img class="shot-dark" src="assets/screenshots/{d}/{shot}-dark.webp" alt="{alt}" width="1080" height="2347" loading="lazy" decoding="async">'
        "</figure>"
    )


def help_article(lang, page):
    c = COMMON[lang]
    p = COPY[lang][page]
    steps = STEPS[page]
    link = help_link(lang)
    pad = " " * 16

    def block(n, title, body, shots):
        num = f'<span class="guide-num" aria-hidden="true">{n}</span>' if n else ""
        phones = ""
        if shots:
            phones = '\n' + pad + '    <div class="guide-phones">' + "".join(help_phone(lang, s) for s in shots) + "</div>"
        return (
            f'{pad}<div class="guide-step">\n'
            f'{pad}    <h3>{num}{inline(title)}</h3>\n'
            f'{pad}    <p>{inline(body, link)}</p>{phones}\n'
            f'{pad}</div>'
        )

    # " <br>" keeps a space in the text, so search results don't run the two lines together.
    title_html = " <br>".join(html.escape(part) for part in p["title"].split("\n"))
    lines = [
        f'            <article class="help-article guide" id="start-{page}">',
        f'{pad}<p class="guide-eyebrow">{html.escape(NAMES[lang][page])}</p>',
        f'{pad}<h1>{title_html}</h1>',
        f'{pad}<p class="guide-lead">{html.escape(p["subtitle"])}</p>',
        f'{pad}<h2>{html.escape(c["start"])}</h2>',
    ]
    if p["start_note"]:
        lines.append(f'{pad}<p class="guide-note">{inline(c["start_note"])}</p>')
    lines += [block(i + 1, t, b, steps["start"][i]) for i, (t, b) in enumerate(p["start"])]
    lines.append(f'{pad}<h2>{html.escape(c["more"])}</h2>')
    lines += [block(None, t, b, steps["more"][i]) for i, (t, b) in enumerate(p["more"])]
    if p["note"]:
        lines.append(f'{pad}<p class="help-callout">{inline(p["note"], link)}</p>')
    lines.append(f'{pad}<h2>{html.escape(HELP_OTHERS[lang])}</h2>')
    lines.append(f'{pad}<div class="help-quicklinks">')
    for o in PAGE_ORDER:
        if o != page:
            lines.append(
                f'{pad}    <a class="help-quicklink" data-target="start-{o}" href="#start-{o}">'
                f'{html.escape(NAMES[lang][o])}<span>{html.escape(COPY[lang][o]["title"].replace(chr(10), " "))}</span></a>'
            )
    lines.append(f'{pad}</div>')
    lines.append("            </article>")
    return "\n".join(lines)


# A tile is ~160px wide on desktop: a long compound gets a soft hyphen so it
# breaks there instead of running out of its tile.
BANNER_SOFT_BREAKS = {"Trainingsprogramm": "Trainings&shy;programm"}


def help_banner(lang):
    """The five guides as tiles, for the top of the Welcome article."""
    b = BANNER[lang]
    pad = " " * 16

    def tile_name(p):
        name = html.escape(NAMES[lang][p])
        for word, broken in BANNER_SOFT_BREAKS.items():
            name = name.replace(word, broken)
        return name

    lines = [
        f'{pad}<section class="guides-banner" aria-labelledby="guides-banner-title">',
        f'{pad}    <p class="guides-banner-eyebrow">{html.escape(HELP_GROUP[lang])}</p>',
        f'{pad}    <h2 id="guides-banner-title">{html.escape(b["title"])}</h2>',
        f'{pad}    <p class="guides-banner-lead">{html.escape(b["lead"])}</p>',
        f'{pad}    <div class="guides-tiles">',
    ]
    for p in PAGE_ORDER:
        lines.append(
            f'{pad}        <a class="guides-tile" data-target="start-{p}" href="#start-{p}">'
            f'<span class="guides-tile-name">{tile_name(p)}</span>'
            f'<span class="guides-tile-desc">{html.escape(b["cards"][p])}</span>'
            f'<span class="guides-tile-go"><span class="guides-tile-go-text">{html.escape(b["go"])} </span>'
            '<span aria-hidden="true">→</span></span></a>'
        )
    lines += [f"{pad}    </div>", f"{pad}</section>"]
    return "\n".join(lines)


def replace_or_insert(text, start, end, block, anchor_before=None):
    """Put `block` between the markers; the first time, insert it on its own line before the anchor."""
    if start in text:
        a = text.index(start)
        b = text.index(end, a) + len(end)
        return text[:a] + block + text[b:]
    if anchor_before is None or text.count(anchor_before) != 1:
        sys.exit(f"anchor not found exactly once: {anchor_before!r}")
    line_start = text.rindex("\n", 0, text.index(anchor_before)) + 1
    return text[:line_start] + "        " + block + "\n" + text[line_start:]


def sync_help():
    for lang, name in HELP_FILES.items():
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        before = text

        css = CSS_START + HELP_CSS + "        " + CSS_END
        text = replace_or_insert(text, CSS_START, CSS_END, css, anchor_before="</style>")

        nav_links = "\n".join(
            f'                    <a class="help-nav-link" data-target="start-{p}" href="#start-{p}">{html.escape(NAMES[lang][p])}</a>'
            for p in PAGE_ORDER
        )
        nav = (
            NAV_START + "\n"
            "                <div class=\"help-nav-group\">\n"
            f"                    <div class=\"help-nav-group-title\">{html.escape(HELP_GROUP[lang])}</div>\n"
            f"{nav_links}\n"
            "                </div>\n"
            "                " + NAV_END
        )
        # After the first nav group (Welcome, Getting Started guide).
        first_group_end = 'href="#getting-started">'
        if NAV_START not in text:
            i = text.index(first_group_end)
            j = text.index("</div>", i) + len("</div>")
            text = text[:j] + "\n                " + nav + text[j:]
        else:
            text = replace_or_insert(text, NAV_START, NAV_END, nav)

        articles = "\n\n".join(help_article(lang, p) for p in PAGE_ORDER)
        art = ART_START + "\n" + articles + "\n            " + ART_END
        if ART_START not in text:
            anchor = '<article class="help-article" id="space-what">'
            if text.count(anchor) != 1:
                sys.exit(f"{name}: space-what article not found once")
            i = text.index(anchor)
            text = text[:i] + art + "\n\n            " + text[i:]
        else:
            text = replace_or_insert(text, ART_START, ART_END, art)

        # The banner opens the Welcome article, above its heading.
        banner = BANNER_START + "\n" + help_banner(lang) + "\n                " + BANNER_END
        if BANNER_START not in text:
            anchor = '<article class="help-article" id="welcome">'
            if text.count(anchor) != 1:
                sys.exit(f"{name}: welcome article not found once")
            i = text.index(anchor) + len(anchor)
            text = text[:i] + "\n                " + banner + text[i:]
        else:
            text = replace_or_insert(text, BANNER_START, BANNER_END, banner)

        if text != before:
            path.write_text(text, encoding="utf-8")
            print("wrote", name)


def main():
    missing = set()
    for steps in STEPS.values():
        for group in steps.values():
            for shots in group:
                for s in shots:
                    for d in ("ko", "en"):
                        for v in ("", "-dark"):
                            f = ROOT / "assets" / "screenshots" / d / f"{s}{v}.webp"
                            if not f.exists():
                                missing.add(str(f.relative_to(ROOT)))
                    if s not in ALT:
                        missing.add("ALT[" + s + "]")
    if missing:
        sys.exit("missing:\n  " + "\n  ".join(sorted(missing)))

    OUT.mkdir(exist_ok=True)
    for lang in LANGS:
        for page in PAGE_ORDER:
            path = OUT / f"{page}{suffix(lang)}.html"
            new = build(lang, page)
            # Keep the footer sync_footer.py stamped in on an earlier run.
            if path.exists():
                old = path.read_text()
                start = "<!-- footer:start"
                if start in old and "<!-- footer:end -->" in old:
                    a = old.index(start)
                    b = old.index("<!-- footer:end -->") + len("<!-- footer:end -->")
                    na = new.index(start)
                    nb = new.index("<!-- footer:end -->") + len("<!-- footer:end -->")
                    new = new[:na] + old[a:b] + new[nb:]
            path.write_text(new)
            print("wrote", path.relative_to(ROOT))

    sync_help()


if __name__ == "__main__":
    main()
