import React from 'react';

export const HighlightLoginSection = ({ title, children, maxWidth = '900px' }) => {
  return (
    <div className="container">
      {title && (
        <h1 className="h2 text-primary text-center mb-4 mt-4 mt-md-6">
          {title}
        </h1>
      )}
      <div
        className="rounded-2 shadow text-center px-3 py-4 px-md-6 py-md-5 mx-auto"
        style={{ backgroundColor: '#FFFDE5', maxWidth: maxWidth }}
      >
        {children}
      </div>
    </div>
  );
};
