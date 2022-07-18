/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./static/*.js", "./templates/*.html"],
    theme: {
        extend: {
            animation: {
                fade: "fadeOut 0.5s ease-in-out",
            },

            keyframes: theme => ({
                fadeOut: {
                    "0%": { opacity: "1" },
                    "100%": { opacity: "0" },
                },
            }),
        },
    },
    plugins: [],
}
