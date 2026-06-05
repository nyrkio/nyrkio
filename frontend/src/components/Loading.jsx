export const Loading = ({loading, text}) => {
  if (loading) {
    return (<div className="loading-spinner">
      <div className="spinner-border text-primary p-0" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      {text ? (<p className="text-primary mt-2">{text}</p>) : ''}
    </div>);
  }
  return (<><div className="loading_done d-none"></div></>);
};