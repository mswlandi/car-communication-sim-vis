const webpack = require('webpack');

module.exports = {
    webpackConfig: {
        resolve: {
            extensions: [ '.ts', '.js' ],
            fallback: {
                "stream": require.resolve("stream-browserify"),
                "buffer": require.resolve("buffer")
            },
            resolve: {
                alias: {
                    process: "process/browser"
                },
            },
        },
        plugins: [
            new webpack.ProvidePlugin({
                Buffer: ['buffer', 'Buffer'],
            }),
            new webpack.ProvidePlugin({
                process: 'process/browser',
            }),
        ],
    }
}