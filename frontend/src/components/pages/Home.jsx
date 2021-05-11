import React from "react";
import UserGuide from "../interfaces/user-guide";
import { motion } from "framer-motion";
import Prices from "../interfaces/crypto-prices";

function Home() {

    const pageVariants = {
        in: {
            opacity: 1
        },
        out: {
            opacity: 0
        }
    }

    const pageTransition = {
        duration: 0.6
    }

    return(
        <motion.div variants={pageVariants} transition={pageTransition} exit="out" animate="in" initial="out" style={{display: "flex", flexDirection: "column", justifyContent: "center", alignContent: "center", textAlign: "center", fontSize: "100%"}}>
            <div className="displaybox-large" style={{textAlign: "center"}}>
                <h1 className="paragraph">ŞAMPİYON BEŞİKTAŞ.</h1>
            </div>
            <Prices />
            <UserGuide />
        </motion.div>)
}

export default Home;
