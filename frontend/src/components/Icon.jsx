export default function Icon({name, className = '', size = 24}) {
  return (
    <svg
      className={`icon ${className}`}
      width={size}
      height={size}
      aria-hidden="true"
    >
      <use href={`#icon-${name}`} />
    </svg>
  );
}
