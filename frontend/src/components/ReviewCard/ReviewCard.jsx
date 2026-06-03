import clsx from 'clsx';
import './ReviewCard.scss'

export const ReviewCard = ({company, loading = 'lazy', variant = 'teaser'}) => {
  const {logo, label, description, links, quoteData} = company;
  const {author, text, link} = quoteData;
  const isFull = variant === 'full';

  return (
    <article
      className={clsx(
        'review-card rounded-2 shadow-sm border border-primary p-4',
        `review-card--${variant}`,
      )}
    >
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
            <div className="text-secondary fw-semibold">
              {author.name}
            </div>

            <div className="fs-6">
              {author.position}
            </div>
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

      {link && !isFull && (
        <div
          className="review-card__link"
          dangerouslySetInnerHTML={{ __html: link }}
        />
      )}

      {!!links?.length && isFull&& (
        <div className="review-card__links">
          <ul className="list-unstyled d-flex flex-wrap gap-2 mb-0 justify-content-end">
            {links.map((item, index) => (
              <li
                key={index}
                dangerouslySetInnerHTML={{
                  __html: item,
                }}
              />
            ))}
          </ul>
        </div>
      )}

      {isFull && (
        <>
          <div className="h5 text-center mt-4">{label}</div>
          {description && (
            <div
              className="review-card__description mt-2"
              dangerouslySetInnerHTML={{
                __html: description,
              }}
            />
          )}
        </>
      )}
    </article>
  );
}
