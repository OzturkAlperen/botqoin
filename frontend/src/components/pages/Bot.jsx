import React, {createRef} from "react";
import { withAuth0 } from '@auth0/auth0-react';
import TextTransition, {presets} from "react-text-transition";
import { motion } from "framer-motion";
import OptionButton from "../interfaces/option-button";
import Guide from "../interfaces/user-guide";
import PercentageIcon from "../../assets/icons/percentage.svg";
import CoinsIcon from "../../assets/icons/coins.svg";
import ArrowsIcon from "../../assets/icons/arrows.svg";

const DisplayBox = (props) => {
    return(
        <div className="displaybox">
            <h1 style={{cursor: "default"}}>{props.name}</h1>
            <p style={{cursor: "default"}}>━━━━━━━━━━━━━━━━━</p>
            <TextTransition
                text={props.data}
                style={{cursor: "default"}}
                springConfig={ presets.stiff }
            />
        </div>
    )
}

class Bot extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            tradePlatform: undefined,
            sellMethod: undefined,
            message: "",
            symbol: "",
            status: ""};
        this.id = null
        this.pp1 = createRef()
        this.pp2 = createRef()
        this.pp3 = createRef()
        this.fq = createRef()
        this.tp = createRef()
        this.ts = createRef()
        this.mti = createRef()
        this.s = createRef()
        this.isStarted = false
        this.triggerBot = this.triggerBot.bind(this)
        this.handlePlatformChange = this.handlePlatformChange.bind(this)
        this.handleMethodChange = this.handleMethodChange.bind(this)

        this.pageVariants = {
            initial: {
                opacity: 0,
                },
            in: {
                opacity: 1,
            },
            out: {
                opacity: 0,
        }
    }

    this.pageTransition = {
        duration: 0.6
    }
}


    async componentDidMount() {

        const { getAccessTokenSilently } = this.props.auth0;
        this.accessToken = await getAccessTokenSilently({
            audience: `botqoin`,
            scope: "read:all",
        })

        await fetch('/api/user/ticket', {
            headers: {
                Authorization: `Bearer ${this.accessToken}`
            },
        })
        .then((respond => respond.json()))
        .then((data) => {
            this.id = data
        })
        .catch((error) => {
            console.log(error);
        });

        this.websocket = new WebSocket(`wss://botqoin.tech/api/websocket/bot/${this.id}`);
        await this.websocketListener()

        window.addEventListener('beforeunload', this.componentCleanup);
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (this.isStarted) {
            this.ts.current.disabled = false
            this.ts.current.style.backgroundColor = "var(--white-accent)"
            this.mti.current.disabled = false
            this.mti.current.style.backgroundColor = "var(--green-accent)"
            this.mti.current.style.pointerEvents = "all"
        } else {
            this.ts.current.disabled = true
            this.ts.current.style.backgroundColor = "#47484D"
            this.mti.current.disabled = true
            this.mti.current.style.backgroundColor = "#47484D"
            this.mti.current.style.pointerEvents = "none"
        }
    }

    componentCleanup() {
        if (this.websocket !== undefined) {
            if (this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.close()
            }
        }
    }

    componentWillUnmount() {
        this.componentCleanup();
        window.removeEventListener('beforeunload', this.componentCleanup);
    }

    async triggerBot() {

        if (this.isStarted) {
            let unsubscribeData = {
                'method': "UNSUBSCRIBE"
            }

            await this.websocket.send(JSON.stringify(unsubscribeData))

            this.isStarted = false
            this.s.current.style.backgroundColor = "#10CB81"

        } else {

            let subscribeData = {
                'method': 'SUBSCRIBE',
                'params': {
                    'profit_percentage_1': this.pp1.current.value,
                    'profit_percentage_2': this.pp2.current.value,
                    'profit_percentage_3': this.pp3.current.value,
                    'trade_platform': this.state.tradePlatform,
                    'trade_pair': this.tp.current.value,
                    'sell_method': this.state.sellMethod,
                    'funds_quantity': this.fq.current.value,
                }
            }

            this.websocket.send(JSON.stringify(subscribeData))
        }
    }

    async websocketListener() {
        this.websocket.onmessage = (event) => {
            const newData = JSON.parse(event.data)
            console.log(newData)
            if (newData.message !== undefined) {
                console.log("a")
                this.setState({message: newData.message})
            }
            if (newData.symbol !== undefined) {
                this.setState({symbol: newData.symbol})
            }
            if (newData.status !== undefined) {
                this.setState({status: newData.status})
            }
            if (newData.signal !== undefined) {
                if (newData.signal === "READY") {
                    this.isStarted = true
                    this.s.current.style.backgroundColor = "#F5475D"
                }
            }
        }
    }

    handlePlatformChange(value) {
        this.setState({tradePlatform: value})
    }

    handleMethodChange(value) {
        this.setState({sellMethod: value})
        if (value === undefined) {
            this.pp2.current.style.width = "0"
            this.pp3.current.style.width = "0"
            this.pp2.current.style.display = "none"
            this.pp3.current.style.display = "none"
        } else if (value === "100") {
            this.pp1.current.style.width = "100%"
            this.pp2.current.style.width = "0"
            this.pp3.current.style.width = "0"
            this.pp1.current.style.display = "block"
            this.pp2.current.style.display = "none"
            this.pp3.current.style.display = "none"
        } else if (value === "5050") {
            this.pp1.current.style.width = "49%"
            this.pp2.current.style.width = "49%"
            this.pp3.current.style.width = "0"
            this.pp1.current.style.display = "block"
            this.pp2.current.style.display = "block"
            this.pp3.current.style.display = "none"
        } else if (value === "502525") {
            this.pp1.current.style.width = "32%"
            this.pp2.current.style.width = "32%"
            this.pp3.current.style.width = "32%"
            this.pp1.current.style.display = "block"
            this.pp2.current.style.display = "block"
            this.pp3.current.style.display = "block"
        }
    }

    render() {
        return(
            <motion.div variants={this.pageVariants} transition={this.pageTransition} exit="out" animate="in" initial="initial" style={{display: "flex", justifyContent: "center", alignItems: "center", alignContent: "stretch", flexWrap: "wrap"}}>
                <DisplayBox name="Message" data={this.state.message}/>
                <DisplayBox name="Symbol" data={this.state.symbol}/>
                <DisplayBox name="Status" data={this.state.status}/>
                <div className="displaybox">
                    <OptionButton buttons={{"Binance": "Binance", "Kucoin": "Kucoin"}} callback={this.handlePlatformChange} buttonClass="platformbutton"/>
                    <OptionButton buttons={{"100": "100", "5050":"50/50", "502525":"50/25/25"}} callback={this.handleMethodChange} buttonClass="methodbutton"/>
                    <span style={{display: "flex", justifyContent: "space-between"}}>
                        <input ref={this.pp1} style={{backgroundImage: `url(${PercentageIcon})`}} className="botinput" placeholder="Profit 1"/>
                        <input ref={this.pp2} style={{backgroundImage: `url(${PercentageIcon})`}} className="botinput" placeholder="Profit 2" />
                        <input ref={this.pp3} style={{backgroundImage: `url(${PercentageIcon})`}} className="botinput" placeholder="Profit 3" />
                    </span>
                    <span style={{display: "flex", justifyContent: "space-between"}}>
                        <input ref={this.fq} style={{backgroundImage: `url(${CoinsIcon})`}} className="botinput" placeholder="Funds Quantity"/>
                    </span>
                    <span style={{display: "flex", justifyContent: "space-between"}}>
                        <input ref={this.tp} style={{backgroundImage: `url(${ArrowsIcon})`}} className="botinput" placeholder="Trade Pair (ie. BTC)"/>
                    </span>
                    <span style={{display: "flex", justifyContent: "space-between"}}>
                        <button ref={this.s} className="generalbutton" style={{backgroundColor: "#10CB81", fontSize: "30px", width: "100%", height: "85px"}} onClick={this.triggerBot}>{this.isStarted ? "Stop" : "Start"}</button>
                    </span>
                    <span style={{display: "flex", justifyContent: "space-between"}}>
                        <input ref={this.ts} style={{backgroundImage: `url(${ArrowsIcon})`, width: "66%"}} className="botinput" placeholder="Trade Symbol"/>
                        <button ref={this.mti} className="generalbutton" style={{width: "32%"}}>Manuel Trade Initialize</button>
                    </span>
                </div>
                <Guide />
            </motion.div>
        )
    }
}

export default withAuth0(Bot)