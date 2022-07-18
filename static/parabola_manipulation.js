function calculateParabolaParameters(x1, y1, x2, y2, x3, y3) {
    denom = (x1 - x2) * (x1 - x3) * (x2 - x3);
    A = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom;
    B = (x3 * x3 * (y1 - y2) + x2 * x2 * (y3 - y1) + x1 * x1 * (y2 - y3)) / denom;
    C = (
        x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3
    ) / denom;

    return [A, B, C];

}


function calculateParabolaEquation(x1, y1, x2, y2, x3, y3) {
    let [A, B, C] = calculateParabolaParameters(x1, y1, x2, y2, x3, y3)
    return () => a * x ** 2 + b * x + c
}
