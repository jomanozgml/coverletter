function maximum_path(node_values) {
    // Determine the height of the pyramid
    let height = Math.floor((Math.sqrt(1 + 8 * node_values.length) - 1) / 2);

    // Build the pyramid structure
    let index = 0;
    let levels = [];
    for (let i = 0; i < height; i++) {
        levels[i] = [];
        for (let j = 0; j <= i; j++) {
            levels[i].push(node_values[index]);
            index++;
        }
    }

    // Dynamic programming to find the maximum path sum, bottom -> up
    for (let i = height - 2; i >= 0; i--) {
        for (let j = 0; j <= i; j++) {
            levels[i][j] += Math.max(levels[i + 1][j], levels[i + 1][j + 1]);
        }
    }

    // The top element of the pyramid now contains the maximum path sum
    return levels[0][0];
}