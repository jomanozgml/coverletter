function valuation(reqArea, area, price) {
    const filteredData = filterOutliers(area, price);
    const filteredArea = filteredData.area;
    const filteredPrice = filteredData.price;

    if (filteredArea.length === 0) {
        return 1000 * reqArea;
    }

    const exactMatches = findExactMatches(reqArea, filteredArea, filteredPrice);
    let valuation;
    if (exactMatches.length > 0) {
        valuation = calculateMean(exactMatches);
    } else {
        const lowerNeighbor = findClosestNeighbor(reqArea, filteredArea, true);
        const higherNeighbor = findClosestNeighbor(reqArea, filteredArea, false);
        if (lowerNeighbor !== null && higherNeighbor !== null) {
            valuation = interpolatePrice(reqArea, lowerNeighbor, higherNeighbor, filteredArea, filteredPrice);
        } else {
            valuation = extrapolatePrice(reqArea, lowerNeighbor || higherNeighbor, filteredArea, filteredPrice);
        }
    }

    return Math.max(1000, Math.min(valuation, 1000000));
}

function filterOutliers(area, price) {
    const pricesByArea = {};
    for (let i = 0; i < area.length; i++) {
        if (!pricesByArea[area[i]]) {
            pricesByArea[area[i]] = [];
        }
        pricesByArea[area[i]].push(price[i]);
    }

    const filteredArea = [];
    const filteredPrice = [];
    for (let i = 0; i < area.length; i++) {
        const prices = pricesByArea[area[i]];
        if (prices.length === 1) {
            filteredArea.push(area[i]);
            filteredPrice.push(price[i]);
        } else {
            const mean = calculateMean(prices);
            const stdDev = calculateStdDev(prices, mean);
            if (Math.abs(price[i] - mean) <= 3 * stdDev) {
                filteredArea.push(area[i]);
                filteredPrice.push(price[i]);
            }
        }
    }

    return { area: filteredArea, price: filteredPrice };
}

function calculateMean(array) {
    const sum = array.reduce((a, b) => a + b, 0);
    return sum / array.length;
}

function calculateStdDev(array, mean) {
    const variance = array.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / array.length;
    return Math.sqrt(variance);
}

function findExactMatches(reqArea, filteredArea, filteredPrice) {
    const exactMatches = [];
    for (let i = 0; i < filteredArea.length; i++) {
        if (filteredArea[i] === reqArea) {
            exactMatches.push(filteredPrice[i]);
        }
    }
    return exactMatches;
}

function findClosestNeighbor(reqArea, filteredArea, isLower) {
    let closestNeighbor = null;
    let closestDiff = Infinity;
    for (const area of filteredArea) {
        const diff = Math.abs(area - reqArea);
        if ((isLower && area < reqArea && diff < closestDiff) ||
                (!isLower && area > reqArea && diff < closestDiff)) {
            closestNeighbor = area;
            closestDiff = diff;
        }
    }
    return closestNeighbor;
}

function interpolatePrice(reqArea, lowerNeighbor, higherNeighbor, filteredArea, filteredPrice) {
    const lowerIndex = filteredArea.indexOf(lowerNeighbor);
    const higherIndex = filteredArea.indexOf(higherNeighbor);
    const lowerPrice = filteredPrice[lowerIndex];
    const higherPrice = filteredPrice[higherIndex];
    const priceDiff = higherPrice - lowerPrice;
    const areaDiff = higherNeighbor - lowerNeighbor;
    const areaRatio = (reqArea - lowerNeighbor) / areaDiff;
    return Math.round(lowerPrice + (areaRatio * priceDiff));
}

function extrapolatePrice(reqArea, neighbor, filteredArea, filteredPrice) {
    const neighborIndex = filteredArea.indexOf(neighbor);
    const neighborPrice = filteredPrice[neighborIndex];
    const filteredAreaWithoutNeighbor = filteredArea.filter(area => area !== neighbor);
    const furthestNeighbor = filteredAreaWithoutNeighbor.reduce((prev, curr) => {
        const prevDiff = Math.abs(prev - reqArea);
        const currDiff = Math.abs(curr - reqArea);
        return currDiff < prevDiff ? curr : prev;
    }, neighbor);
    const furthestNeighborIndex = filteredArea.indexOf(furthestNeighbor);
    const furthestNeighborPrice = filteredPrice[furthestNeighborIndex];
    const areaDiff = Math.abs(reqArea - neighbor);
    const furthestAreaDiff = Math.abs(reqArea - furthestNeighbor);
    const priceDiff = furthestNeighborPrice - neighborPrice;
    const areaRatio = areaDiff / (areaDiff + furthestAreaDiff);
    return Math.round(neighborPrice + (areaRatio * priceDiff));
}