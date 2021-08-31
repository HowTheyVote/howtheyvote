// The radius of the circle the pupils should move along
const RADIUS = 10;

// Hardcoded dimensions of the eye/white ellipsis. As we're
// using SVG symbols, the actual DOM elements are placed inside
// a shadow DOM which makes it impossible to get the dimensions
// dynamically.
const WIDTH = 35;
const HEIGHT = 45;

export default eye => ({
  centerX: 0,
  centerY: 0,
  cursorX: 0,
  cursorY: 0,

  init() {
    this.setCenterPosition();
  },

  get translate() {
    // Relative position of the cursor from the center of the eye
    const deltaX = this.cursorX - this.centerX;
    const deltaY = this.cursorY - this.centerY;

    const angle = Math.atan2(deltaX, deltaY);

    // Point on circumference of a circle around the center of the eye
    const x = Math.round(RADIUS * Math.sin(angle));
    const y = Math.round(RADIUS * Math.cos(angle));

    const absX = Math.abs(deltaX);
    const absY = Math.abs(deltaY);

    // If the cursor is inside of the circle, use the cursor position,
    // i.e. this clamps the values between -1 * |delta| and |delta|.
    return {
      x: Math.max(-1 * absX, Math.min(x, absX)),
      y: Math.max(-1 * absY, Math.min(y, absY)),
    };
  },

  setCursorPosition(event) {
    this.cursorX = event.pageX;
    this.cursorY = event.pageY;
  },

  setCenterPosition() {
    const { x, y } = this.$el.getBoundingClientRect();

    this.centerX = x + WIDTH / 2;
    this.centerY = y + HEIGHT / 2;
  },
});
