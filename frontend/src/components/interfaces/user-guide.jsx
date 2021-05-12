import React from "react";

const UserGuide = () => {
    return(
        <div className="displaybox-large">
                <h1>How to use botqoin?</h1>
                <ol>
                    <li>Choose the platform you want to execute trade.</li>
                    <li>Set a sell method.
                        <ul>
                            <li>100 means all of the purchased tokens will be sold as a single piece at the desired profit percentage</li>
                            <li>50/50 means the half of the purchased token amount will be sold at first desired profit percentage and the other will be sold at second set proift percentage.</li>
                            <li>50/25/25 means the first half will be sold at first set profit percentage, the other and will be splitted in a half again will be sold at second and third set profit percentages.</li>
                        </ul>
                    </li>
                    <li>Put in target profit percentages.
                        <ul>
                            <li>Use the first input filed if you choose 100 option</li>
                            <li>If you choose 50/50 use the first two input fields</li>
                            <li>If you choose 50/25/25 option then first input field is for half of the purchased tokens, second and third one is for quarter pieces.</li>
                        </ul>
                    </li>
                    <li>
                        Input trade quantity. This is the quote currency amount that will be used while executing the buy order.
                    </li>
                    <li>
                        Input trade pair, also known as quote currency.
                    </li>
                    <li>
                        Press start button, after that bot will be started.
                    </li>
                    <li>
                        After the bot has started, you can set the trade symbol manually if the auto scraper fails to get symbol name from incoming messages. And when you press the "Initialize Manuel Trade" button bot will execute the buy and sell orders without the need of symbol name fetch.
                    </li>
                </ol>
            </div>
    )
}

export default UserGuide