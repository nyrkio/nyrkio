import './UserCard.scss';
import { SmallLogo } from "./../Logo";

export const UserCard = ({ profile = {} }) => {
  const {
    image,
    position,
    name,
    description
  } = profile;

  if (!name && !position && !description && !image) {
    return null;
  }

  return (
    <div className="user-card border border-primary rounded-2 shadow p-3 p-md-4">

      <div className="user-card__image rounded-2 overflow-hidden ratio ratio-2x3">
        {image?.src ? (
          <img
            className="img-fluid object-fit-cover"
            src={image.src}
            alt={image.alt || (name ? `${name} photo` : "User image")}
            width={image.width}
            height={image.height}
            loading={image.loading || "lazy"}
          />
        ) : (
          <div className="d-flex justify-content-center align-items-center">
            <SmallLogo loading="lazy" className="w-50"/>
          </div>
        )}
      </div>


      {(name || position || description) && (
        <div className="user-card__content">
          {name && (
            <div className="user-card__name text-secondary fw-semibold">
              {name}
            </div>
          )}

          {position && (
            <div className="user-card__position text-muted fs-6">
              {position}
            </div>
          )}

          {description && (
            <div
              className="user-card__description mt-3"
              dangerouslySetInnerHTML={{ __html: description }}
            />
          )}
        </div>
      )}
    </div>
  );
};
