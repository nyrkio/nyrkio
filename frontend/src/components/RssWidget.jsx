import { useEffect, useState } from "react";
import * as rssParser from 'react-native-rss-parser';


export const RssWidget = () => {
  const [rssFeed, setRssFeed] = useState([]);
  const readRss = async () => {
    return fetch('https://blog.nyrkio.com/feed')
      .then((response) => response.text())
      .then((responseData) => rssParser.parse(responseData))
      .then((rss) => {
            setRssFeed(rss.items);

      });

  };

  const [loading, setLoading] = useState(true);
  useEffect(()=>{
    setLoading(true);
    readRss()
    .then(()=>{console.log("done");})
    .catch((err)=>{console.error(err);})
    .finally(()=>setLoading(false));
  },[]);

  const RssListItems = ({feed}) => {
    return feed.slice(0,4).map((item)=>{
        //console.log(item);
        const d = new Date(Date.parse(item.published));
        return (<div key={item.id} className="col col-md-3 col-xs-12 col-sm-6">
                                <a href={item.links[0].url}>{item.title}</a>{" "}
                                <span className="author">{item.authors[0].name}</span>{" "}
                                <span className="date">{d.toISOString().substring(0,10)}</span>{" "}</div>);
    });
  };
  return (
    <>
    <div className="rss-widget nyrkio-blog blog-rss-widget row">
      {loading ? "" : (
      <>
      <div className="row nyrkio-blog-header">
        <p>Recently on <a href="https://blog.nyrkio.com">blog.nyrkio.com</a>:</p>
      </div>
      <div className="row nyrkio-blog-body">
        <RssListItems feed={rssFeed} />
      </div>
      </>
    )}
    </div>
    </>
  );
};
