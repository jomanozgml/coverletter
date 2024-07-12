function calcMissing(readings) {
    // Write your code here
    // Let's gather up the timestamps, readings, and those pesky missing values
    const timestamps = [];
    const levels = [];

    // Time to break down the data and skip the first line as it holds the length of the readings
    for (let i = 1; i < readings.length; i++) {
        const [timestamp, level] = readings[i].split("\t");
        timestamps.push(timestamp);

        if (String(level).startsWith("Missing"))  {
            levels.push(level); // Keep track of missing values
        } else {
            levels.push(parseFloat(level)); // Parse the readings as floats
        }
    }

    let levelsLength = levels.length;

    // Function to estimate missing values based on what's around them (like connecting the dots)
    function estimateMissingValue(index) {
        if (index === 0) {
            // First missing value? Check the next reading if we have it
            let nextIndex = 1;
            let next = levels[nextIndex];
            while (String(next).startsWith("Missing")) {
                nextIndex++;
                next = levels[nextIndex];
                if (nextIndex >= levelsLength) {
                    next = 0;
                    break;
                }
            }
            return next;
        } else if (index === levelsLength - 1) {
            // Last missing value? Look back at the previous reading if possible
            return levels[levelsLength - 2]
        } else {
            // Not the first or last? Take an average of the readings before and after
            const previous = levels[index - 1];
            let nextIndex = index + 1;
            let next = levels[nextIndex];
            while (String(next).startsWith("Missing")) {
                nextIndex++;
                next = levels[nextIndex];
                if (nextIndex >= levelsLength) {
                    next = previous;
                    break;
                }
            }
            return (previous + next) / 2;
        }
    }

    // Estimate missing values and show the results
    for (let i = 0; i < levelsLength; i++) {
        if (String(levels[i]).startsWith("Missing")) {
            const estimatedValue = estimateMissingValue(i);
            levels[i] = estimatedValue;
            console.log(estimatedValue.toFixed(2));
        }
    }
}