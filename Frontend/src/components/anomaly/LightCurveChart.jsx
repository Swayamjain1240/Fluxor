import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip
} from "recharts";


const LightCurveChart = ({ lightCurve = [] }) => {

    if (!lightCurve.length) {

        return (

            <div
                style={{
                    padding: "40px",

                    textAlign: "center",

                    color: "#7f8796",

                    background: "#11151d",

                    borderRadius: "12px",

                    border: "1px solid #272d39"
                }}
            >

                No light curve data available.

            </div>
        );
    }


    return (

        <div
            style={{
                width: "100%",

                height: "420px",

                background: "#11151d",

                border: "1px solid #272d39",

                borderRadius: "12px",

                padding: "20px"
            }}
        >

            <h3
                style={{
                    marginTop: 0
                }}
            >
                Photometric Light Curve
            </h3>


            <ResponsiveContainer
                width="100%"
                height="90%"
            >

                <LineChart
                    data={
                        lightCurve
                    }
                >

                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#252b35"
                    />


                    <XAxis
                        dataKey="time"
                        tick={{
                            fill: "#8991a1",
                            fontSize: 11
                        }}
                    />


                    <YAxis
                        dataKey="flux"
                        tick={{
                            fill: "#8991a1",
                            fontSize: 11
                        }}
                    />


                    <Tooltip
                        contentStyle={{
                            background: "#11151d",

                            border:
                                "1px solid #353c49",

                            borderRadius:
                                "8px"
                        }}
                    />


                    <Line
                        type="monotone"
                        dataKey="flux"
                        dot={false}
                        strokeWidth={1.4}
                    />

                </LineChart>

            </ResponsiveContainer>

        </div>
    );
};


export default LightCurveChart;