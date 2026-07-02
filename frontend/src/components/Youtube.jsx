import PropTypes from "prop-types";
import "./Youtube.css";

export const YoutubeEmbed = ({ embedId }) => (
  <div className="ratio ratio-7x10 mx-auto my-4" style={{ maxWidth: "560px" }}>
    <iframe
      width="566"
      height="803"
      src={`https://www.youtube.com/embed/${embedId}?autoplay=1&mute=1&loop=1&playlist=${embedId}`}
      frameBorder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
      title="Embedded youtube"
    />
  </div>
);

YoutubeEmbed.propTypes = {
  embedId: PropTypes.string.isRequired,
};
