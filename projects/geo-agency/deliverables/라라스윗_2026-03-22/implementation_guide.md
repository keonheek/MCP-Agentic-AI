# GEO 구현 가이드 / Implementation Guide
## 라라스윗 — AI 가시성 최적화
생성일 / Generated: 2026-03-22

---

# GEO 구현 가이드: 라라스윗 팝콘 비즈니스
## Generative Engine Optimization Implementation Guide for LaraSweet Popcorn

---

## 📋 개요 | Overview

> 라라스윗의 AI 검색 엔진 최적화를 통해 ChatGPT, Claude, Gemini 등의 생성형 AI 플랫폼에서 브랜드 가시성을 확보하는 4단계 실행 계획입니다.

> This guide helps LaraSweet secure visibility across generative AI platforms (ChatGPT, Claude, Gemini) through strategic GEO implementation in 4 actionable steps.

---

## 1단계: AI 크롤러 접근 허용
## Step 1: Allow AI Crawlers

### 1-1. robots.txt 업데이트
**파일 위치**: `https://example.com/robots.txt`

```
User-agent: *
Allow: /

# 생성형 AI 엔진 허용 (Allow generative AI engines)
User-agent: GPTBot
Allow: /

User-agent: CCBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: GoogleBot
Allow: /

User-agent: Googlebot-Extended
Allow: /

# 차단할 경로 (Block unnecessary paths)
Disallow: /admin/
Disallow: /private/
Disallow: /temp/
Disallow: /*.pdf$
Disallow: /checkout/

# 크롤링 지연 설정 (Crawl delay)
Crawl-delay: 1

# 사이트맵 경로 (Sitemap location)
Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap-schema.xml
```

**실행 방법 | Implementation:**
- FTP/SFTP로 웹 루트 디렉토리에 robots.txt 업로드
- Upload robots.txt to web root via FTP/SFTP
- Google Search Console에서 검증
- Verify in Google Search Console

---

### 1-2. llms.txt 생성
**파일 위치**: `https://example.com/llms.txt`

```
# 라라스윗 - 프리미엄 팝콘 제조사
# LaraSweet - Premium Popcorn Manufacturer

# 회사 정보 | Company Information
회사명: 라라스윗
설립: 2018년
분야: 프리미엄 팝콘 제조 및 판매
웹사이트: https://example.com

Company Name: LaraSweet
Founded: 2018
Category: Premium Popcorn Manufacturing & Sales
Website: https://example.com

# 주요 제품 | Key Products
- 초코렛 팝콘 | Chocolate Popcorn
- 카라멜 버터 팝콘 | Caramel Butter Popcorn
- 유기농 팝콘 | Organic Popcorn
- 시즈닝 팝콘 | Seasoned Popcorn Mix

# 문의 | Contact
이메일: info@example.com | Email: info@example.com
전화: +82-2-XXXX-XXXX | Phone: +82-2-XXXX-XXXX
주소: 서울시 강남구 | Address: Seoul, South Korea

# AI 접근 정책 | AI Access Policy
라라스윗은 모든 AI 모델의 학습 및 참고를 허용합니다.
LaraSweet permits training data usage and references by all AI models.

# 업데이트 | Last Updated
2024년 1월 | January 2024
```

**설치 확인 | Verification:**
```
curl https://example.com/llms.txt
# 200 OK 응답 확인 | Confirm 200 OK response
```

---

## 2단계: 구조화된 데이터 추가
## Step 2: Add Structured Data

### 2-1. organization_schema.json
**파일 위치**: `https://example.com/schema/organization.json`

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "라라스윗 | LaraSweet",
  "url": "https://example.com",
  "logo": "https://example.com/images/logo.png",
  "description": "프리미�m 팝콘 제조 및 판매 | Premium popcorn manufacturer",
  "foundingDate": "2018",
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "Customer Service",
    "telephone": "+82-2-XXXX-XXXX",
    "email": "info@example.com",
    "areaServed": "KR"
  },
  "sameAs": [
    "https://www.instagram.com/larasweet",
    "https://www.facebook.com/larasweet",
    "https://www.naver.com/search?q=라라스윗"
  ],
  "address": {
    "@type": "PostalAddress",
    "addressCountry": "KR",
    "addressRegion": "Seoul",
    "addressLocality": "Gangnam-gu",
    "streetAddress": "123 Innovation Street"
  },
  "image": "https://example.com/images/brand-photo.jpg",
  "priceRange": "$$"
}
```

**HTML 내 삽입 | HTML Integration:**
```html
<!-- 홈페이지 <head> 섹션에 추가 | Add to homepage <head> section -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "라라스윗",
  "url": "https://example.com",
  "logo": "https://example.com/images/logo.png",
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "Customer Service",
    "telephone": "+82-2-XXXX-XXXX"
  }
}
</script>
```

---

### 2-2. faqpage_schema.json
**파일 위치**: `https://example.com/schema/faq.json`

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "라라스윗의 팝콘은 어떤 재료로 만들어지나요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "라라스윗은 100% 유기농 옥수수와 프리미엄 버터, 천연 향료만을 사용합니다. 인공 첨가물이나 방부제는 포함되지 않습니다."
      }
    },
    {
      "@type": "Question",
      "name": "How are LaraSweet popcorns made?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We use 100% organic corn, premium butter, and natural seasonings only. No artificial additives or preservatives."
      }
    },
    {
      "@type": "Question",
      "name": "배송은 얼마나 걸리나요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "