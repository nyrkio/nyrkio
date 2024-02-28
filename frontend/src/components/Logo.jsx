import defaultLogo from '../static/logo/full/Brown/NyrkioLogo_Final_Full_Brown-800px.png';
import smallLogo from '../static/logo/full/Brown/NyrkioLogo_Final_Full_Brown-200px.png';

export const Logo =  ( ) => {
        return (
            <div className="nyrkio-logo nyrkio-logo-default">
            <img src={defaultLogo} alt="Nyrkiö (logo)" className="nyrkio-logo-img nyrkio-logo-img-default" />
            </div>
        );
}

export const SmallLogo =  ( ) => {
        return (
            <div className="nyrkio-logo nyrkio-logo-default">
            <img src={smallLogo} alt="Nyrkiö (logo)" className="nyrkio-logo-img nyrkio-logo-img-small " />
            </div>
        );
}
