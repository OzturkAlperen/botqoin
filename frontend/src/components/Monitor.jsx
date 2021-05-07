import React, { useState, useEffect, useMemo, useRef } from 'react';
import useWebSocket from 'react-use-websocket';
import {useAuth0} from "@auth0/auth0-react";
import {Link} from "react-router-dom";
import TextTransition, { presets } from "react-text-transition";

const Monitor = () => {

    const { getAccessTokenSilently } = useAuth0();

    const id = Math.random().toString(36).slice(2);
    const [socketURL, setSocketURL] = useState(null);
    const messageHistory = useRef([]);
    const {lastJsonMessage} = useWebSocket(socketURL);
    messageHistory.current = useMemo(() => messageHistory.current.concat(lastJsonMessage),[lastJsonMessage]);

    //const [message, setMessage] = useState('')
    //const [symbol, setSymbol] = useState('')
    const [status, setStatus] = useState('Please input desired profit percentage and order quantity and then press start.')

    const [percentage1, setPercentage1] = useState('')
    const [percentage2, setPercentage2] = useState('')
    const [percentage3, setPercentage3] = useState('')
    const [quantity, setQuantity] = useState('')
    const [pair, setPair] = useState('')
    const [platform, setPlatform] = useState("")
    const [sellmethod, setSellMethod] = useState("100")
    const [manuelsymbol, setManuelSymbol] = useState("")

    const [job, setJob] = useState("Start")
    const [djob, setDJob] = useState("Start")

    // Styling States
    const [bbgcolor, setBBGColor] = useState("#F5475D")
    const [kbgcolor, setKBGColor] = useState("#F5475D")
    const [sbgcolor, setSBGColor] = useState("#10CB81")
    const [mbgcolor, setMBGColor] = useState("#3B3F41")
    const [pbgcolor, setPBGColor] = useState("#3B3F41")
    const [mstate, setMState] = useState("none")
    const [pstate, setPState] = useState("none")
    const [p100color, setP100Color] = useState("#10CB81")
    const [p5050color, setP5050Color] = useState("#F5475D")
    const [p502525color, setP502525Color] = useState("#F5475D")
    const [p1status, setP1Status] = useState("block")
    const [p2status, setP2Status] = useState("none")
    const [p3status, setP3Status] = useState("none")
    const [p1width, setP1Width] = useState("100%")
    const [p2width, setP2Width] = useState()
    const [p3width, setP3Width] = useState()


    // Inline Styling
    const percentageStyle1 = {
        backgroundImage: "url('./assets/icons/percentage.png')",
        backgroundSize: "20px",
        backgroundPosition: "5px 8px",
        backgroundColor: "#EFB90A",
        display: `${p1status}`,
        paddingLeft: "30px",
        fontSize: "15px",
        height: "35px",
        width: `${p1width}`,
    }

    const percentageStyle2 = {
        backgroundImage: "url('./assets/icons/percentage.png')",
        backgroundSize: "20px",
        backgroundPosition: "5px 8px",
        backgroundColor: "#EFB90A",
        display: `${p2status}`,
        paddingLeft: "30px",
        fontSize: "15px",
        height: "35px",
        width: `${p2width}`,
    }

    const percentageStyle3 = {
        backgroundImage: "url('./assets/icons/percentage.png')",
        backgroundSize: "20px",
        backgroundPosition: "5px 8px",
        backgroundColor: "#EFB90A",
        display: `${p3status}`,
        paddingLeft: "30px",
        fontSize: "15px",
        height: "35px",
        width: `${p3width}`,
    }

    const quantityStyle = {
        backgroundImage: "url('./assets/icons/coins.png')",
        backgroundSize: "20px",
        backgroundPosition: "5px 8px",
        backgroundRepeat: "no-repeat",
        backgroundColor: "#efb90a",
        paddingLeft: "30px",
        height: "35px",
        fontSize: "15px",
        width: "100%",
    }

    const pairStyle = {
        backgroundImage: "url('./assets/icons/arrows.png')",
        backgroundSize: "20px",
        backgroundPosition: "5px 8px",
        backgroundRepeat: "no-repeat",
        backgroundColor: "#efb90a",
        paddingLeft: "30px",
        height: "35px",
        fontSize: "15px",
        width: "100%",
    }

    const symbolStyle = {
        backgroundImage: "url('./assets/icons/arrows.png')",
        backgroundSize: "20px",
        backgroundPosition: "5px 8px",
        backgroundRepeat: "no-repeat",
        backgroundColor: "#efb90a",
        paddingLeft: "30px",
        height: "35px",
        fontSize: "15px",
        width: "49%",
    }

    const selectStyleBinance = {
        background: `${bbgcolor}`,
        fontSize: "14px",
        width: "49%",
        height: "35px",
    }

    const selectStyleKucoin = {
        backgroundColor: `${kbgcolor}`,
        fontSize: "14px",
        width: "49%",
        height: "35px",
    }

    const sellStyle100 = {
        background: `${p100color}`,
        width: "32%",
        height: "25px",
    }

    const sellStyle5050 = {
        background: `${p5050color}`,
        width: "32%",
        height: "25px",
    }

    const sellStyle502525 = {
        background: `${p502525color}`,
        width: "32%",
        height: "25px",
    }

    const startStyle = {
        background: `${sbgcolor}`,
        fontSize: "30px",
        width: "100%",
        height: "auto",
    }

    const prepumpStyle = {
        background: `${pbgcolor}`,
        fontSize: "16px",
        width: "100%",
        height: "35px",
        pointerEvents: `${pstate}`,
    }

    const manuelStyle = {
        background: `${mbgcolor}`,
        fontSize: "14px",
        width: "49%",
        height: "35px",
        pointerEvents: `${mstate}`,
    }

    const boxStyle = {
        fontFamily: "'Ubuntu', sans-serif",
        textAlign: "left",
        background: "#12161B",
        color: "#ffffff",
        borderRadius: "12px",
        padding: "15px",
        margin: "1%",
        flex: "1 2 300px",
        boxSizing: "border-box",
        height: "400px",
    }

    const boxStyleLarge = {
        fontFamily: "'Ubuntu', sans-serif",
        textAlign: "left",
        background: "#12161B",
        color: "#ffffff",
        borderRadius: "12px",
        padding: "20px",
        margin: "1%",
        flex: "1 2 100%",
        boxSizing: "border-box",
        marginBottom: "auto",
    }

    // Page Load & Cleanup | useEffect
    useEffect(() => {

        return () => {
            const cleanUp = async () => {

                const accessToken = await getAccessTokenSilently({
                    audience: `botqoin`,
                    scope: "read:all",
                });

                setSocketURL(null)

                fetch('/api/closedown', {
                    headers: {
                        Authorization: `Bearer ${accessToken}`
                    },
                })
                .catch((error) => {
                    console.log(error);
                });

                setJob("Start")
                setSBGColor("#10CB81")
            }
            cleanUp().then(null)
        }

    }, [getAccessTokenSilently])

    // Start Button | triggerJob
    const triggerJob = async () => {

        if (job === "Start") {

            setStatus("Starting up.")

            const accessToken = await getAccessTokenSilently({
                    audience: `botqoin`,
                    scope: "read:all",
                });

            let botInfo = {
                'profit_percentage_1': percentage1,
                'profit_percentage_2': percentage2,
                'profit_percentage_3': percentage3,
                'sell_method': sellmethod,
                'funds_quantity': quantity,
                'trade_pair': pair,
                'trade_platform': platform
            }

            fetch('/api/startup', {
                method: 'post',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(botInfo),
            })
                .then((respond => respond.json()))
                .then((data) => {
                    if (data.message === "success") {
                        setSocketURL(`ws://18.183.39.189/ws/${id}`)
                        setJob("Stop")
                        setSBGColor("#F5475D")
                        setPBGColor("#10CB81")
                        setMBGColor("#10CB81")
                        setPState("all")
                        setMState("all")
                    } else if (data.result === "fail") {
                        setStatus("An Error Occured")
                    } else {
                        //pass
                    }
                })
                .catch((error) => {
                    console.log(error);
                });

        } else {

            const accessToken = await getAccessTokenSilently({
                    audience: `botqoin`,
                    scope: "read:all",
                });

            fetch('/api/closedown', {
                headers: {
                    Authorization: `Bearer ${accessToken}`
                },
            })
            .catch((error) => {
                console.log(error);
            });
            setSocketURL(null)
            setStatus("Process stopped.")
            setJob("Start");
            setSBGColor("#10CB81")
            setPBGColor("#3B3F41")
            setMBGColor("#3B3F41")
            setPState("none")
            setMState("none")
        }
    }

    const triggerManuel = () => {
        let opts = {
                'symbol': manuelsymbol,
            }

        fetch('/api/manueltrade', {
                method: 'post',
                headers: {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify(opts),
            })
                .then((respond => respond.json()))
                .then((data) => {
                    console.log(data)
                })
                .catch((error) => {
                    console.log(error);
                });
    }

    const triggerDetector = () => {

        if (djob === "Start" && job === "Stop") {
           fetch('/api/detector_startup', {
                credentials: "include",
           })
               .then((respond => respond.json()))
               .then((data) => {
                   if (data.result === "success") {
                       setDJob("Stop")
                       setPBGColor("#F5475D")
                   }
               })
               .catch((error) => {
                    console.log(error);
               });
        } else if (djob === "Stop" && job === "Stop") {
            fetch('/api/detector_closedown', {
                credentials: "include",
            })
                .then((respond => respond.json()))
                .then((data) => {
                    if (data.result === "success") {
                       setDJob("Start")
                       setPBGColor("#10CB81")
                    }
                })
                .catch((error) => {
                    console.log(error);
                });
        }

    }

    // Input Change Handlers
    const handlePercentageChange1 = (value) => {
        setPercentage1(value.target.value)
    }

    const handlePercentageChange2 = (value) => {
        setPercentage2(value.target.value)
    }

    const handlePercentageChange3 = (value) => {
        setPercentage3(value.target.value)
    }

    const handleQuantityChange = (value) => {
        setQuantity(value.target.value)
    }

    const handlePairChange = (value) => {
        setPair(value.target.value)
    }

    const handleManuelSymbolChange = (value) => {
        setManuelSymbol(value.target.value)
    }



    // Button Click Handlers | Binance&Kucoin
    const selectBinance = () => {
        setPlatform("Binance")
        setBBGColor("#10CB81")
        setKBGColor("#F5475D")
    }

    const selectKucoin = () => {
        setPlatform("Kucoin")
        setKBGColor("#10CB81")
        setBBGColor("#F5475D")
    }

    const select100 = () => {
        setSellMethod("100")
        setP100Color("#10CB81")
        setP5050Color("#F5475D")
        setP502525Color("#F5475D")
        setP1Status("block")
        setP2Status("none")
        setP3Status("none")
        setP1Width("100%")
        setP2Width("0%")
        setP3Width("0%")
    }

    const select5050 = () => {
        setSellMethod("5050")
        setP5050Color("#10CB81")
        setP100Color("#F5475D")
        setP502525Color("#F5475D")
        setP1Status("block")
        setP2Status("block")
        setP3Status("none")
        setP1Width("49%")
        setP2Width("49%")
        setP3Width("0%")
    }

    const select502525 = () => {
        setSellMethod("502525")
        setP502525Color("#10CB81")
        setP100Color("#F5475D")
        setP5050Color("#F5475D")
        setP1Status("block")
        setP2Status("block")
        setP3Status("block")
        setP1Width("32%")
        setP2Width("32%")
        setP3Width("32%")
    }

    return (
        <div style={{display: "flex", justifyContent: "center", alignItems: "center", alignContent: "stretch", flexWrap: "wrap"}}>
            <Link to="/settings">
                    <button className="menubutton" style={{position: "absolute", right: "150px", top: "20px"}}>Settings</button>
            </Link>
            <div style={boxStyle}>
                <h1 style={{cursor: "default"}}>Message</h1>
                <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
                <TextTransition
                    text={lastJsonMessage ? lastJsonMessage.message : ""}
                    style={{cursor: "default"}}
                    springConfig={ presets.stiff }
                />
            </div>
            <div style={boxStyle}>
                <h1 style={{cursor: "default"}}>Symbol</h1>
                <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
                <TextTransition
                    text={lastJsonMessage ? lastJsonMessage.symbol : ""}
                    style={{cursor: "default"}}
                    springConfig={ presets.stiff }
                />
            </div>
            <div style={boxStyle}>
                <h1 style={{cursor: "default"}}>Status</h1>
                <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
                <TextTransition
                    text={lastJsonMessage ? lastJsonMessage.status : status}
                    style={{cursor: "default"}}
                    springConfig={ presets.stiff }
                />
            </div>
            <div style={boxStyle}>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <button className="generalbutton" style={selectStyleBinance} onClick={selectBinance}>Binance</button>
                    <button className="generalbutton" style={selectStyleKucoin} onClick={selectKucoin}>Kucoin</button>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <button className="generalbutton" style={sellStyle100} onClick={select100}>100</button>
                    <button className="generalbutton" style={sellStyle5050} onClick={select5050}>50/50</button>
                    <button className="generalbutton" style={sellStyle502525} onClick={select502525}>50/25/25</button>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <input className="generalinput" style={percentageStyle1} type="text" placeholder="Profit 1" onChange={handlePercentageChange1} value={percentage1}/>
                    <input className="generalinput" style={percentageStyle2} type="text" placeholder="Profit 2" onChange={handlePercentageChange2} value={percentage2}/>
                    <input className="generalinput" style={percentageStyle3} type="text" placeholder="Profit 3" onChange={handlePercentageChange3} value={percentage3}/>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <input className="generalinput" style={quantityStyle} type="text" placeholder="Order Quantity" onChange={handleQuantityChange} value={quantity}/>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <input className="generalinput" style={pairStyle} type="text" placeholder="Trade Pair (ex. BTC)" onChange={handlePairChange} value={pair}/>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <button className="generalbutton" style={startStyle} onClick={triggerJob}>{job}</button>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <button className="generalbutton" style={prepumpStyle} onClick={triggerDetector}>Prepump Detector</button>
                </span>
                <span style={{display: "flex", justifyContent: "space-between"}}>
                    <input className="generalinput" style={symbolStyle} type="text" placeholder="Manuel Symbol" onChange={handleManuelSymbolChange} value={manuelsymbol}/>
                    <button className="generalbutton" style={manuelStyle} onClick={triggerManuel}>Manuel Trade</button>
                </span>
            </div>
            <div style={boxStyleLarge}>
                <h1>How to use botqoin?</h1>
                <ol>
                    <li>Choose the platform you want perform trade.</li>
                    <li>Set a sell method.
                        <ul>
                            <li>100 means all of the purchased tokens will be sold as a single piece at the desired profit percentage</li>
                            <li>50/50 means the half of the purchased token amount will be sold at first desired profit percentage and the other will be sold at second set proift percentage.</li>
                            <li>50/25/25 means the first half will be sold at first set profit percentage, the other and will be splitted in a half again will be sold at second and third set profit percentages.</li>
                        </ul>
                    </li>
                    <li>Put in desired profit percentages.
                        <ul>
                            <li>Use the first input filed if you choose 100 option</li>
                            <li>If you choose 50/50 use the first two input fields</li>
                            <li>If you choose 50/25/25 option then first input field is for half of the purchased tokens, second and third one is for quarter pieces.</li>
                        </ul>
                    </li>
                    <></>
                </ol>
            </div>
        </div>
    )
}

export default Monitor