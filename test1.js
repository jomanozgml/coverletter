function valuation(reqArea, area, price) {
    const filteredData = filterOutliers(area, price);
    const filteredArea = filteredData.area;
    const filteredPrice = filteredData.price;

    if (filteredArea.length === 0) {
        return 1000 * reqArea;
    }

    const exactMatches = findExactMatches(reqArea, filteredArea);
    const lowerNeighbor = findClosestNeighbor(reqArea, filteredArea, true);
    const higherNeighbor = findClosestNeighbor(reqArea, filteredArea, false);

    let valuation;
    if (exactMatches.length > 0) {
        valuation = calculateMean(exactMatches, filteredPrice);
    } else if (lowerNeighbor && higherNeighbor) {
        valuation = interpolatePrice(reqArea, lowerNeighbor, higherNeighbor, filteredArea, filteredPrice);
    } else {
        valuation = extrapolatePrice(reqArea, lowerNeighbor || higherNeighbor, filteredArea, filteredPrice);
    }

    return Math.max(1000, Math.min(valuation, 1000000));
}

function filterOutliers(area, price) {
    const filteredData = { area: [], price: [] };
    for (let i = 0; i < area.length; i++) {
        const currentArea = area[i];
        const currentPrice = price[i];
        let isOutlier = false;

        const compList = [];
        for (let j = 0; j < area.length; j++) {
            if (j !== i && area[j] === currentArea) {
                compList.push(price[j]);
            }
        }

        if (compList.length > 0) {
            const meanPrice = calculateMean(compList);
            const stdDev = calculateStandardDeviation(compList, meanPrice);
            isOutlier = Math.abs(currentPrice - meanPrice) > 3 * stdDev;
        }

        if (!isOutlier) {
            filteredData.area.push(currentArea);
            filteredData.price.push(currentPrice);
        }
    }
    return filteredData;
}

function findExactMatches(reqArea, filteredArea) {
    return filteredArea.filter(area => area === reqArea);
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

function calculateMean(data) {
    const sum = data.reduce((acc, val) => acc + val, 0);
    return sum / data.length;
}

function calculateStandardDeviation(data, mean) {
    const squaredDiffs = data.map(val => Math.pow(val - mean, 2));
    const variance = calculateMean(squaredDiffs);
    return Math.sqrt(variance);
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
