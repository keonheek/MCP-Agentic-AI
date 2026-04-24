/**
 * 경제학 개론 — Google Forms 자동 생성 스크립트
 *
 * 사용법: createAllForms() 실행
 * 결과: Google Drive에 챕터별 퀴즈 폼 자동 생성
 */

// 챕터별 폼 제목
var CHAPTER_TITLES = {
  "1": "경제학 개론 — 제1장: 경제학의 10대 기본원리",
  "2": "경제학 개론 — 제2장: 경제학자처럼 생각하기",
  "3": "경제학 개론 — 제3장: 상호의존관계와 교역의 이득",
  "4": "경제학 개론 — 제4장: 시장의 수요와 공급",
  "5": "경제학 개론 — 제5장: 탄력성",
  "6": "경제학 개론 — 제6장: 수요, 공급과 정부정책",
  "7": "경제학 개론 — 제7장: 소비자, 생산자, 시장의 효율성",
  "8": "경제학 개론 — 제8장: 조세의 경제적 비용",
  "9": "경제학 개론 — 제9장: 국제무역"
};

// 정답 문자 → 인덱스 변환
var ANSWER_INDEX = { "A": 0, "B": 1, "C": 2, "D": 3 };

// Run this first — creates chapters 1 and 2 only
function createForms_Ch1_2() {
  createFormsForChapters(["1", "2"]);
}

function createAllForms() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Questions");
  if (!sheet) {
    SpreadsheetApp.getUi().alert("시트 이름이 'Questions'인지 확인하세요.");
    return;
  }

  var data = sheet.getDataRange().getValues();
  // 헤더 제거
  var rows = data.slice(1);

  // 챕터별로 질문 그룹화
  var chapters = {};
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var chapter = String(row[0]).trim();
    if (!chapter) continue;

    if (!chapters[chapter]) chapters[chapter] = [];
    chapters[chapter].push({
      question:    String(row[1]).trim(),
      choiceA:     String(row[2]).trim(),
      choiceB:     String(row[3]).trim(),
      choiceC:     String(row[4]).trim(),
      choiceD:     String(row[5]).trim(),
      answer:      String(row[6]).trim().toUpperCase(),
      explanation: String(row[7]).trim()
    });
  }

  // 챕터별 폼 생성
  var createdLinks = [];
  var chapterNums = Object.keys(chapters).sort(function(a, b) {
    return parseInt(a) - parseInt(b);
  });

  for (var c = 0; c < chapterNums.length; c++) {
    var ch = chapterNums[c];
    var title = CHAPTER_TITLES[ch] || ("경제학 개론 — 제" + ch + "장");
    var questions = chapters[ch];

    var form = FormApp.create(title);
    form.setIsQuiz(true);
    form.setTitle(title);
    form.setDescription(
      "각 문제를 읽고 가장 적절한 답을 선택하세요.\n" +
      "제출 후 정답과 해설을 확인할 수 있습니다."
    );
    form.setCollectEmail(false);
    form.setShowLinkToRespondAgain(true);
    form.setPublishingSummary(true);

    for (var q = 0; q < questions.length; q++) {
      var qData = questions[q];
      var item = form.addMultipleChoiceItem();

      item.setTitle(qData.question);
      item.setRequired(true);

      var choices = [
        item.createChoice(qData.choiceA, ANSWER_INDEX[qData.answer] === 0),
        item.createChoice(qData.choiceB, ANSWER_INDEX[qData.answer] === 1),
        item.createChoice(qData.choiceC, ANSWER_INDEX[qData.answer] === 2),
        item.createChoice(qData.choiceD, ANSWER_INDEX[qData.answer] === 3)
      ];
      item.setChoices(choices);

      item.setPoints(1);

      // 오답 피드백
      item.setFeedbackForIncorrect(
        FormApp.createFeedback()
          .setText("틀렸습니다.\n정답: " + qData.answer + "\n\n해설: " + qData.explanation)
          .build()
      );

      // 정답 피드백
      item.setFeedbackForCorrect(
        FormApp.createFeedback()
          .setText("정답입니다!")
          .build()
      );
    }

    var url = form.getPublishedUrl();
    createdLinks.push("제" + ch + "장: " + url);
    Logger.log("제" + ch + "장 생성 완료: " + url);
  }

  // 결과 요약 출력
  var summary = "✅ 폼 생성 완료!\n\n";
  summary += createdLinks.join("\n");
  summary += "\n\n(Apps Script 로그에서도 확인 가능)";

  SpreadsheetApp.getUi().alert(summary);
}

/**
 * 모의고사 폼 생성 (3회분)
 * createAllForms() 실행 후 별도로 실행
 */
function createMockExams() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("MockExams");
  if (!sheet) {
    SpreadsheetApp.getUi().alert("'MockExams' 시트가 없습니다. README 참고.");
    return;
  }

  var data = sheet.getDataRange().getValues();
  var rows = data.slice(1);

  var exams = {};
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var examNum = String(row[0]).trim();
    if (!examNum) continue;

    if (!exams[examNum]) exams[examNum] = [];
    exams[examNum].push({
      question:    String(row[1]).trim(),
      choiceA:     String(row[2]).trim(),
      choiceB:     String(row[3]).trim(),
      choiceC:     String(row[4]).trim(),
      choiceD:     String(row[5]).trim(),
      answer:      String(row[6]).trim().toUpperCase(),
      explanation: String(row[7]).trim()
    });
  }

  var examTitles = {
    "1": "경제학 개론 모의고사 1회 — 기본 (목표: 20/25)",
    "2": "경제학 개론 모의고사 2회 — 실전 (목표: 22/25)",
    "3": "경제학 개론 모의고사 3회 — 심화 (목표: 24/25)"
  };

  var links = [];
  var examNums = Object.keys(exams).sort();

  for (var e = 0; e < examNums.length; e++) {
    var num = examNums[e];
    var title = examTitles[num] || ("모의고사 " + num + "회");
    var questions = exams[num];

    var form = FormApp.create(title);
    form.setIsQuiz(true);
    form.setTitle(title);
    form.setDescription("시간: 50분 / 25문제\n제출 후 정답 확인 가능");
    form.setCollectEmail(false);
    form.setShowLinkToRespondAgain(true);

    for (var q = 0; q < questions.length; q++) {
      var qData = questions[q];
      var item = form.addMultipleChoiceItem();

      item.setTitle((q + 1) + ". " + qData.question);
      item.setRequired(true);

      var choices = [
        item.createChoice(qData.choiceA, ANSWER_INDEX[qData.answer] === 0),
        item.createChoice(qData.choiceB, ANSWER_INDEX[qData.answer] === 1),
        item.createChoice(qData.choiceC, ANSWER_INDEX[qData.answer] === 2),
        item.createChoice(qData.choiceD, ANSWER_INDEX[qData.answer] === 3)
      ];
      item.setChoices(choices);
      item.setPoints(1);

      item.setFeedbackForIncorrect(
        FormApp.createFeedback()
          .setText("틀렸습니다.\n정답: " + qData.answer + "\n\n해설: " + qData.explanation)
          .build()
      );
      item.setFeedbackForCorrect(
        FormApp.createFeedback().setText("정답입니다!").build()
      );
    }

    links.push(num + "회: " + form.getPublishedUrl());
    Logger.log("모의고사 " + num + "회 생성 완료");
  }

  var summary = "✅ 모의고사 폼 생성 완료!\n\n" + links.join("\n");
  SpreadsheetApp.getUi().alert(summary);
}
