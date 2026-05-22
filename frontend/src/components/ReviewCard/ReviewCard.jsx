import React from 'react';
import './ReviewCard.scss'

export default function ReviewCard({ quoteData, logo, loading = 'lazy' }) {
  const {
    author,
    text,
    link,
  } = quoteData;

  return (
    <article className="review-card rounded-2 shadow-sm border border-primary p-4">
      <div className="review-card__header d-flex flex-column flex-lg-row align-items-md-center justify-content-between gap-3 mb-3">
        <div className="review-card__author">
          <img
            className="review-card__image shadow"
            loading={loading}
            src={author.image.src}
            alt={author.image.alt}
            width={author.image.width}
            height={author.image.height}
          />

          <div>
            <div className="text-secondary fw-semibold ">{author.name}</div>
            {(author.position || author.company) && (<div className="fs-6">{[author.position, author.company].filter(Boolean).join(', ')}</div>)}
          </div>
        </div>
        <img
          className="review-card__logo mx-auto mx-md-0"
          loading={loading}
          src={logo.src}
          alt={logo.alt}
          width={logo.width}
          height={logo.height}
        />
      </div>

      <blockquote className="review-card__quote">
        “{text}”
      </blockquote>

      {link && (
        <div
          className="review-card__link"
          dangerouslySetInnerHTML={{ __html: link }}
        />
      )}
    </article>
  );
}
