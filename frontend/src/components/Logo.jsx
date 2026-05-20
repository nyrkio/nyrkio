export const Logo = () => {
  return (
    <div className="nyrkio-logo nyrkio-logo-default">
    <img
    src="/p/logo/full/new/NyrkioLogo_Final_Full_Brown46-shadow-300.png"
    alt="Nyrkiö (logo)"
    className="nyrkio-logo-img nyrkio-logo-img-default"
    />
    </div>
  );
};
export const LogoBrown = () => {
  return (
    <div className="nyrkio-logo nyrkio-logo-brown">
    <img
    src="/p/logo/full/new/NyrkioLogo_Final_Full_Brown46-shadow-300.png"
    alt="Nyrkiö (logo)"
    className="nyrkio-logo-img nyrkio-logo-img-brown"
    />
    </div>
  );
};

export const SmallLogo = ({loading='eager'}) => {
  return (
    <div className="nyrkio-logo nyrkio-logo-default" >
      <img
        loading={loading}
        src="/p/logo/full/new/NyrkioLogo_Final_Full_Brown46-shadow-300.png"
        alt="Nyrkiö (logo)"
        title="Nyrkiö"
        className="d-block img-fluid nyrkio-logo-img nyrkio-logo-img-small nyrkio-logo-img-default"
      />
    </div>
  );
};

export const LogoSlogan = () => {
  return (
    <div className="container-fluid text-center nyrkio-title nyrkio-logo nyrkio-logo-default">
    <img
    src="/p/logo/full/new/NyrkioLogo_Final_Full_Brown46-shadow-300.png"
    alt="Nyrkiö (logo)"
    className="nyrkio-logo-img nyrkio-logo-img-small "
    />
    <h1><span className="git">Continuous Benchmarking</span><span className="for"> as a Service</span></h1>
    </div>
  );
};
export const Slogan = (text = false) => {
  if (text) {
    return (<>Continuous Benchmarking</>);
  }
  else {
    return (
      <div className="container-fluid text-center nyrkio-title nyrkio-logo nyrkio-logo-default">
        <h1><span className="git">Continuous Benchmarking</span><span className="for"> as a Service</span></h1>
      </div>
    );
  }

};
export const LogoBrownSlogan = () => {
  return (
    <div className="container-fluid text-center nyrkio-title nyrkio-logo nyrkio-logo-default">
    <img
    src="/p/logo/full/new/NyrkioLogo_Final_Full_Brown46-shadow-300.png"
    alt="Nyrkiö (logo)"
    className="nyrkio-logo-img nyrkio-logo-img-small "
    />
    <h1>Continuous Benchmarking</h1>
    </div>
  );
};

export const LogoSloganNarrow = () => {
  return (
    <div className="container-fluid text-center nyrkio-title nyrkio-logo nyrkio-logo-default col-sm-12 col-md-10">
      <img
        src="/p/logo/full/new/NyrkioLogo_Final_Full_Brown46-shadow-300.png"
        alt="Nyrkiö (logo)"
        className="nyrkio-logo-img nyrkio-logo-img-small "
      />
      <h1>Continuous Benchmarking</h1>
    </div>
  );
};

export const SloganNarrow = () => {
  return (
    <div className="container-fluid text-center nyrkio-title nyrkio-logo nyrkio-logo-default col-sm-12 col-md-10">
    <h1>Continuous Benchmarking</h1>
    </div>
  );
};
