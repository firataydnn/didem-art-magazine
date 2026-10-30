# ATELIER — Editorial publishing contract

The public site reads `data/approved-stories.json`. This file currently contains no approved articles. Never generate approvals automatically.

## Required story fields

```json
{
  "slug": "unique-ascii-story-slug",
  "title": "A verified, editorially approved headline",
  "category": "SERGİLER",
  "body": "Original, fact-checked article text (at least 500 characters)",
  "image": "assets/images/licensed-photo.jpg",
  "image_credit": "Creator, copyright owner, licence, and any required attribution",
  "source_url": "https://official-source.example/article",
  "approved_at": "2026-10-30T15:00:00+03:00"
}
```

`approved_at` must be recorded only by an authenticated editorial approval action. The site filters incomplete records, but **client-side checks are not authorization**. A trusted backend must enforce editorial roles and maintain an audit log.

## Workflow

1. Ingest source leads into a **private** draft store, with original URLs, publication dates, and rights notes.
2. Verify claims and image reuse rights; write original editorial text.
3. Editor reviews, edits, rejects, or explicitly approves each story.
4. A trusted server exports **approved-only** records to `data/approved-stories.json` and deploys the site.
5. Check the live page, mobile layout, sources, image credits, and search indexing.

## Remaining launch blockers

- Authenticated editorial dashboard and server-side authorization
- Private draft database and audit trail
- Automated approved-only export/deploy pipeline
- Licensed image inventory and image provenance review
- Production URL, build and mobile smoke tests
- Remove `noindex,nofollow` **only after** editorial launch sign-off

Do not place credentials, unpublished drafts, or private editorial notes in the public GitHub repository.
