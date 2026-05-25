import React from "react";
import "./PricingCard.scss";
export const PricingCard = ({
    title,
    subtitle,
    pricing: { price, period, tax = "+Tax" },
    short = false,
    className,
    children
  }) => {
  return (
    <div className={`card card--pricing border-primary ${className}`}>
      <div className="card-title-badge badge h4 text-bg-secondary mx-auto mb-1">
        {title}
      </div>
      {(subtitle) && (
        <div className="card-pricing__subtitle"> {subtitle}</div>
      )}

      <div className="card-pricing my-5">
        <span className="card-pricing__price">{price}</span>&nbsp;
        <span className="card-pricing__period">{period}</span>
        <span className="card-pricing__tax">{tax}</span>
      </div>

      {React.Children.map(children, (child) => {
        if (!child) return null;
        if (short && child.type === PricingCard.FeatureList) {
          return null;
        }
        return child;
      })}
    </div>
  );
};

PricingCard.FeatureList = ({ children }) => {
  return <ul className="list-unstyled list-checkmark mt-3 mb-4">{children}</ul>;
};

PricingCard.CTA = ({ children }) => {
  return <div className="card-pricing__cta">{children}</div>;
};
