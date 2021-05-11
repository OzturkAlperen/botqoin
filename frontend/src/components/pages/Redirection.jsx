import React from "react";
import { motion } from "framer-motion";

const Redirection = () => {

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

    return (
            <motion.div variants={pageVariants} transition={pageTransition} exit="out" animate="in" initial="out" style={{position: "relative", top: "25vh", transform: "translateY(-50%)", textAlign: "center", fontSize: "80%"}}>
                <h1 key="2" className="paragraph">Please wait.</h1>
                <h1 key="3" className="paragraph">You are being redirected.</h1>
            </motion.div>
    )
}

export default Redirection