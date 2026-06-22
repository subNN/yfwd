/* ============================================
 * 一饭为定 - 登录/注册页共享脚本
 * 提供 AnimatedCharacters 动画角色组件
 * ============================================ */

const { createApp, ref, computed, watch, onMounted, onUnmounted, h, defineComponent } = Vue;

/* ---------- 眼球（带眼白）组件 ---------- */
const EyeBall = defineComponent({
  name: 'EyeBall',
  props: {
    size: { type: Number, default: 18 },
    pupilSize: { type: Number, default: 7 },
    maxDistance: { type: Number, default: 5 },
    eyeColor: { type: String, default: 'white' },
    pupilColor: { type: String, default: '#2D2D2D' },
    isBlinking: { type: Boolean, default: false },
    isSad: { type: Boolean, default: false },
    sadRotate: { type: Number, default: 0 },
    forceLookX: { type: Number, default: undefined },
    forceLookY: { type: Number, default: undefined },
  },
  setup(props) {
    const eyeRef = ref(null);
    const mouseX = ref(0);
    const mouseY = ref(0);

    const handleMouseMove = (e) => {
      mouseX.value = e.clientX;
      mouseY.value = e.clientY;
    };

    const pupilPosition = computed(() => {
      if (props.forceLookX !== undefined && props.forceLookY !== undefined) {
        return { x: props.forceLookX, y: props.forceLookY };
      }
      if (!eyeRef.value) return { x: 0, y: 0 };
      const eye = eyeRef.value.getBoundingClientRect();
      const cx = eye.left + eye.width / 2;
      const cy = eye.top + eye.height / 2;
      const dx = mouseX.value - cx;
      const dy = mouseY.value - cy;
      const dist = Math.min(Math.sqrt(dx * dx + dy * dy), props.maxDistance);
      const angle = Math.atan2(dy, dx);
      return { x: Math.cos(angle) * dist, y: Math.sin(angle) * dist };
    });

    onMounted(() => window.addEventListener('mousemove', handleMouseMove));
    onUnmounted(() => window.removeEventListener('mousemove', handleMouseMove));

    return () => h('div', {
      ref: eyeRef,
      class: ['eyeball', { 'eyeball--sad': props.isSad }],
      style: {
        width: `${props.size}px`,
        height: props.isBlinking ? '2px' : (props.isSad ? `${props.size * 0.5}px` : `${props.size}px`),
        backgroundColor: props.eyeColor,
        borderRadius: props.isSad ? `0 0 ${props.size}px ${props.size}px` : '50%',
        transform: props.isSad ? `rotate(${props.sadRotate}deg)` : 'rotate(0deg)',
      }
    }, !props.isBlinking ? [
      h('div', {
        class: 'pupil',
        style: {
          width: `${props.pupilSize}px`,
          height: `${props.pupilSize}px`,
          backgroundColor: props.pupilColor,
          transform: `translate(${pupilPosition.value.x}px, ${props.isSad ? -1 : pupilPosition.value.y}px)`,
        }
      })
    ] : []);
  }
});

/* ---------- 瞳孔（无眼白，黑色实心）组件 ---------- */
const Pupil = defineComponent({
  name: 'Pupil',
  props: {
    size: { type: Number, default: 12 },
    maxDistance: { type: Number, default: 5 },
    pupilColor: { type: String, default: '#2D2D2D' },
    isBlinking: { type: Boolean, default: false },
    forceLookX: { type: Number, default: undefined },
    forceLookY: { type: Number, default: undefined },
  },
  setup(props) {
    const pupilRef = ref(null);
    const mouseX = ref(0);
    const mouseY = ref(0);

    const handleMouseMove = (e) => {
      mouseX.value = e.clientX;
      mouseY.value = e.clientY;
    };

    const pupilPosition = computed(() => {
      if (props.forceLookX !== undefined && props.forceLookY !== undefined) {
        return { x: props.forceLookX, y: props.forceLookY };
      }
      if (!pupilRef.value) return { x: 0, y: 0 };
      const p = pupilRef.value.getBoundingClientRect();
      const cx = p.left + p.width / 2;
      const cy = p.top + p.height / 2;
      const dx = mouseX.value - cx;
      const dy = mouseY.value - cy;
      const dist = Math.min(Math.sqrt(dx * dx + dy * dy), props.maxDistance);
      const angle = Math.atan2(dy, dx);
      return { x: Math.cos(angle) * dist, y: Math.sin(angle) * dist };
    });

    onMounted(() => window.addEventListener('mousemove', handleMouseMove));
    onUnmounted(() => window.removeEventListener('mousemove', handleMouseMove));

    return () => h('div', {
      ref: pupilRef,
      class: 'pupil',
      style: {
        width: `${props.size}px`,
        height: props.isBlinking ? '2px' : `${props.size}px`,
        backgroundColor: props.pupilColor,
        transform: `translate(${pupilPosition.value.x}px, ${pupilPosition.value.y}px)`,
      }
    });
  }
});

/* ---------- 动画角色组件 ---------- */
const AnimatedCharacters = defineComponent({
  name: 'AnimatedCharacters',
  components: { EyeBall, Pupil },
  props: {
    isTyping: Boolean,
    showPassword: Boolean,
    passwordLength: { type: Number, default: 0 },
    loginFailed: Boolean,
    loginSuccess: Boolean,
  },
  setup(props) {
    const purpleRef = ref(null);
    const blackRef = ref(null);
    const orangeRef = ref(null);
    const yellowRef = ref(null);
    const hasEntered = ref(false);

    const isPurpleBlinking = ref(false);
    const isBlackBlinking = ref(false);
    const isOrangeBlinking = ref(false);
    const isYellowBlinking = ref(false);
    const isLookingAtEachOther = ref(false);
    const isPurplePeeking = ref(false);

    const purplePos = ref({ faceX: 0, faceY: 0, bodySkew: 0 });
    const blackPos = ref({ faceX: 0, faceY: 0, bodySkew: 0 });
    const orangePos = ref({ faceX: 0, faceY: 0, bodySkew: 0 });
    const yellowPos = ref({ faceX: 0, faceY: 0, bodySkew: 0 });

    const isHidingPassword = computed(() => props.passwordLength > 0 && !props.showPassword);

    const confettiColors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A78BFA', '#FF9B6B', '#6BCB77', '#4D96FF'];
    const confettiStyles = ref([]);
    const showConfetti = ref(false);
    const successLookY = ref(-5);
    let confettiTimeout = null;
    let successLookAnimId = null;

    const generateConfetti = () => {
      confettiStyles.value = Array.from({ length: 140 }, (_, i) => ({
        left: `${Math.random() * 100}%`,
        top: `-${10 + Math.random() * 30}%`,
        backgroundColor: confettiColors[i % confettiColors.length],
        width: `${4 + Math.random() * 6}px`,
        height: `${8 + Math.random() * 12}px`,
        animationDelay: `${Math.random() * 2}s`,
        animationDuration: `${4.5 + Math.random() * 2}s`,
        transform: `rotate(${Math.random() * 360}deg)`,
      }));
      showConfetti.value = true;
      if (confettiTimeout) clearTimeout(confettiTimeout);
      confettiTimeout = setTimeout(() => {
        showConfetti.value = false;
        confettiStyles.value = [];
      }, 8000);
    };

    const animateSuccessLook = () => {
      const startY = -5, endY = 4, duration = 5500, startTime = performance.now();
      const step = (now) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = progress < 0.5
          ? 4 * progress * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 3) / 2;
        successLookY.value = startY + (endY - startY) * eased;
        if (progress < 1) successLookAnimId = requestAnimationFrame(step);
      };
      successLookAnimId = requestAnimationFrame(step);
    };

    watch(() => props.loginSuccess, (val) => {
      if (val) {
        generateConfetti();
        successLookY.value = -5;
        if (successLookAnimId) cancelAnimationFrame(successLookAnimId);
        animateSuccessLook();
      } else {
        successLookY.value = -5;
        if (successLookAnimId) cancelAnimationFrame(successLookAnimId);
      }
    });

    let purpleBlinkTimeout, blackBlinkTimeout, orangeBlinkTimeout, yellowBlinkTimeout;
    let lookingTimeout, peekTimeout;

    const characterCenters = ref({
      purple: { x: 0, y: 0 },
      black: { x: 0, y: 0 },
      orange: { x: 0, y: 0 },
      yellow: { x: 0, y: 0 },
    });

    const updateCharacterCenters = () => {
      const map = { purple: purpleRef, black: blackRef, orange: orangeRef, yellow: yellowRef };
      for (const key in map) {
        const el = map[key].value;
        if (el) {
          const rect = el.getBoundingClientRect();
          characterCenters.value[key] = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 3 };
        }
      }
    };

    const calculatePosition = (cx, cy, mx, my, rangeX = 15, rangeY = 10, minX = null, maxX = null, minY = null, maxY = null) => {
      const rMinX = minX !== null ? minX : -rangeX;
      const rMaxX = maxX !== null ? maxX : rangeX;
      const rMinY = minY !== null ? minY : -rangeY;
      const rMaxY = maxY !== null ? maxY : rangeY;
      const dx = mx - cx, dy = my - cy;
      const scaleX = Math.max(Math.abs(rMinX), Math.abs(rMaxX));
      const scaleY = Math.max(Math.abs(rMinY), Math.abs(rMaxY));
      const faceX = Math.max(rMinX, Math.min(rMaxX, dx / (300 / scaleX)));
      const faceY = Math.max(rMinY, Math.min(rMaxY, dy / (300 / scaleY)));
      const bodySkew = Math.max(-6, Math.min(6, -dx / 120));
      return { faceX, faceY, bodySkew };
    };

    let rafId = null;
    let pendingMouseX = 0, pendingMouseY = 0, needsUpdate = false;

    const updatePositions = () => {
      if (needsUpdate && hasEntered.value) {
        needsUpdate = false;
        const { purple, black, orange, yellow } = characterCenters.value;
        purplePos.value = calculatePosition(purple.x, purple.y, pendingMouseX, pendingMouseY, 0, 0, -46, 18, -8, 5);
        blackPos.value = calculatePosition(black.x, black.y, pendingMouseX, pendingMouseY);
        orangePos.value = calculatePosition(orange.x, orange.y, pendingMouseX, pendingMouseY, 0, 0, -46, 20, -18, 20);
        yellowPos.value = calculatePosition(yellow.x, yellow.y, pendingMouseX, pendingMouseY);
      }
      rafId = requestAnimationFrame(updatePositions);
    };

    const handleMouseMove = (e) => {
      pendingMouseX = e.clientX;
      pendingMouseY = e.clientY;
      needsUpdate = true;
    };

    const scheduleBlink = (ref, name) => {
      const interval = Math.random() * 4000 + 3000;
      const t = setTimeout(() => {
        ref.value = true;
        setTimeout(() => {
          ref.value = false;
          scheduleBlink(ref, name);
        }, 150);
      }, interval);
      if (name === 'purple') purpleBlinkTimeout = t;
      if (name === 'black') blackBlinkTimeout = t;
      if (name === 'orange') orangeBlinkTimeout = t;
      if (name === 'yellow') yellowBlinkTimeout = t;
    };

    watch(() => props.isTyping, (newVal) => {
      if (newVal) {
        isLookingAtEachOther.value = true;
        if (lookingTimeout) clearTimeout(lookingTimeout);
        lookingTimeout = setTimeout(() => { isLookingAtEachOther.value = false; }, 800);
      } else {
        isLookingAtEachOther.value = false;
        if (lookingTimeout) clearTimeout(lookingTimeout);
      }
    });

    watch([() => props.passwordLength, () => props.showPassword], ([length, show]) => {
      if (length > 0 && show) {
        if (peekTimeout) clearTimeout(peekTimeout);
        const interval = Math.random() * 3000 + 2000;
        peekTimeout = setTimeout(() => {
          isPurplePeeking.value = true;
          setTimeout(() => { isPurplePeeking.value = false; }, 800);
        }, interval);
      } else {
        isPurplePeeking.value = false;
        if (peekTimeout) clearTimeout(peekTimeout);
      }
    });

    onMounted(() => {
      window.addEventListener('mousemove', handleMouseMove, { passive: true });
      window.addEventListener('resize', updateCharacterCenters, { passive: true });
      scheduleBlink(isPurpleBlinking, 'purple');
      scheduleBlink(isBlackBlinking, 'black');
      scheduleBlink(isOrangeBlinking, 'orange');
      scheduleBlink(isYellowBlinking, 'yellow');

      setTimeout(() => {
        hasEntered.value = true;
        updateCharacterCenters();
        rafId = requestAnimationFrame(updatePositions);
      }, 1400);
    });

    onUnmounted(() => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', updateCharacterCenters);
      if (purpleBlinkTimeout) clearTimeout(purpleBlinkTimeout);
      if (blackBlinkTimeout) clearTimeout(blackBlinkTimeout);
      if (orangeBlinkTimeout) clearTimeout(orangeBlinkTimeout);
      if (yellowBlinkTimeout) clearTimeout(yellowBlinkTimeout);
      if (lookingTimeout) clearTimeout(lookingTimeout);
      if (peekTimeout) clearTimeout(peekTimeout);
      if (successLookAnimId) cancelAnimationFrame(successLookAnimId);
      if (rafId) cancelAnimationFrame(rafId);
      if (confettiTimeout) clearTimeout(confettiTimeout);
    });

    /* 暴露给模板的工具：根据状态返回表情位置/类型 */
    const eyeStyle = (color, baseLeft, baseTop) => {
      const passOpen = props.passwordLength > 0 && props.showPassword;
      const lookAt = isLookingAtEachOther.value;
      const left = passOpen ? baseLeft.peekLeft : (lookAt ? baseLeft.centerLeft : `${baseLeft.normalLeft + color.faceX}px`);
      const top = passOpen ? baseTop.peekTop : (lookAt ? baseTop.centerTop : `${baseTop.normalTop + color.faceY}px`);
      return { left, top };
    };

    const mouthStyle = (color, baseLeft, baseTop) => {
      const passOpen = props.passwordLength > 0 && props.showPassword;
      const lookAt = isLookingAtEachOther.value;
      const left = passOpen ? baseLeft.peekLeft : (lookAt ? baseLeft.centerLeft : `${baseLeft.normalLeft + color.faceX}px`);
      const top = passOpen ? baseTop.peekTop : (lookAt ? baseTop.centerTop : `${baseTop.normalTop + color.faceY}px`);
      return { left, top };
    };

    const bodyTransform = (color) => {
      if (!hasEntered.value) return undefined;
      const passOpen = props.passwordLength > 0 && props.showPassword;
      if (passOpen) return 'skewX(0deg)';
      if (isLookingAtEachOther.value) return `skewX(${(color.bodySkew || 0) - 12}deg) translateX(40px)`;
      if (props.isTyping || isHidingPassword.value) return `skewX(${(color.bodySkew || 0) - 12}deg) translateX(40px)`;
      return `skewX(${color.bodySkew || 0}deg)`;
    };

    const purpleBody = computed(() => ({
      transform: bodyTransform(purplePos.value),
      height: (props.isTyping || isHidingPassword.value) ? '440px' : '400px',
    }));
    const blackBody = computed(() => ({
      transform: hasEntered.value
        ? ((props.passwordLength > 0 && props.showPassword)
            ? 'skewX(0deg)'
            : isLookingAtEachOther.value
              ? `skewX(${(blackPos.value.bodySkew || 0) * 1.5 + 10}deg) translateX(20px)`
              : (props.isTyping || isHidingPassword.value)
                ? `skewX(${(blackPos.value.bodySkew || 0) * 1.5}deg)`
                : `skewX(${blackPos.value.bodySkew || 0}deg)`)
        : undefined,
    }));
    const orangeBody = computed(() => ({
      transform: hasEntered.value
        ? ((props.passwordLength > 0 && props.showPassword) ? 'skewX(0deg)' : `skewX(${orangePos.value.bodySkew || 0}deg)`)
        : undefined,
    }));
    const yellowBody = computed(() => ({
      transform: hasEntered.value
        ? ((props.passwordLength > 0 && props.showPassword) ? 'skewX(0deg)' : `skewX(${yellowPos.value.bodySkew || 0}deg)`)
        : undefined,
    }));

    const typing = computed(() => (props.isTyping || isHidingPassword.value) && !props.loginFailed && !props.loginSuccess);
    const sad = computed(() => props.loginFailed);
    const happy = computed(() => props.loginSuccess);

    return () => h('div', { class: 'animated-characters-container' }, [
      // 五彩纸屑
      showConfetti.value ? h('div', { class: 'confetti-container' },
        confettiStyles.value.map((s, i) => h('div', { key: i, class: 'confetti-piece', style: s }))
      ) : null,

      // 紫色 - 后面
      h('div', {
        ref: purpleRef,
        class: ['character', 'purple-character', { 'entrance-complete': hasEntered.value }],
        style: { left: '70px', width: '180px', backgroundColor: '#6C3FF5', borderRadius: '0', zIndex: 1, ...purpleBody.value }
      }, [
        h('div', {
          class: 'eyes',
          style: eyeStyle(purplePos.value, { normalLeft: 75, centerLeft: '85px', peekLeft: '50px' }, { normalTop: 25, centerTop: '50px', peekTop: '20px' })
        }, [
          h(EyeBall, { size: 18, pupilSize: 7, maxDistance: 5, eyeColor: 'white', pupilColor: '#2D2D2D', isBlinking: isPurpleBlinking.value,
            forceLookX: props.loginSuccess ? 0 : ((props.passwordLength > 0 && props.showPassword) ? (isPurplePeeking.value ? 4 : -4) : (isLookingAtEachOther.value ? 3 : undefined)),
            forceLookY: props.loginSuccess ? successLookY.value : ((props.passwordLength > 0 && props.showPassword) ? (isPurplePeeking.value ? 5 : -4) : (isLookingAtEachOther.value ? 4 : undefined)) }),
          h(EyeBall, { size: 18, pupilSize: 7, maxDistance: 5, eyeColor: 'white', pupilColor: '#2D2D2D', isBlinking: isPurpleBlinking.value,
            forceLookX: props.loginSuccess ? 0 : ((props.passwordLength > 0 && props.showPassword) ? (isPurplePeeking.value ? 4 : -4) : (isLookingAtEachOther.value ? 3 : undefined)),
            forceLookY: props.loginSuccess ? successLookY.value : ((props.passwordLength > 0 && props.showPassword) ? (isPurplePeeking.value ? 5 : -4) : (isLookingAtEachOther.value ? 4 : undefined)) }),
        ]),
        h('div', {
          class: ['purple-mouth-shape', { 'purple-mouth-shape--typing': typing.value, 'purple-mouth-shape--sad': sad.value, 'purple-mouth-shape--happy': happy.value }],
          style: mouthStyle(purplePos.value, { normalLeft: 97, centerLeft: '106px', peekLeft: '72px' }, { normalTop: 57, centerTop: '82px', peekTop: '57px' })
        })
      ]),

      // 黑色 - 中间
      h('div', {
        ref: blackRef,
        class: ['character', 'black-character', { 'entrance-complete': hasEntered.value }],
        style: { left: '240px', width: '120px', height: '310px', backgroundColor: '#2D2D2D', borderRadius: '0', zIndex: 2, ...blackBody.value }
      }, [
        h('div', {
          class: 'eyes',
          style: eyeStyle(blackPos.value, { normalLeft: 26, centerLeft: '32px', peekLeft: '10px' }, { normalTop: 32, centerTop: '12px', peekTop: '28px' })
        }, [
          h(EyeBall, { size: 16, pupilSize: 6, maxDistance: 4, eyeColor: 'white', pupilColor: '#2D2D2D', isBlinking: isBlackBlinking.value, isSad: sad.value, sadRotate: -20,
            forceLookX: props.loginSuccess ? 0 : ((props.passwordLength > 0 && props.showPassword) ? -4 : (isLookingAtEachOther.value ? 0 : undefined)),
            forceLookY: props.loginSuccess ? successLookY.value : ((props.passwordLength > 0 && props.showPassword) ? -4 : (isLookingAtEachOther.value ? -4 : undefined)) }),
          h(EyeBall, { size: 16, pupilSize: 6, maxDistance: 4, eyeColor: 'white', pupilColor: '#2D2D2D', isBlinking: isBlackBlinking.value, isSad: sad.value, sadRotate: 20,
            forceLookX: props.loginSuccess ? 0 : ((props.passwordLength > 0 && props.showPassword) ? -4 : (isLookingAtEachOther.value ? 0 : undefined)),
            forceLookY: props.loginSuccess ? successLookY.value : ((props.passwordLength > 0 && props.showPassword) ? -4 : (isLookingAtEachOther.value ? -4 : undefined)) }),
        ])
      ]),

      // 橙色 - 前左
      h('div', {
        ref: orangeRef,
        class: ['character', 'orange-character', { 'entrance-complete': hasEntered.value }],
        style: { left: '0px', width: '240px', height: '150px', zIndex: 3, backgroundColor: '#FF9B6B', borderRadius: '120px 120px 0 0', ...orangeBody.value }
      }, [
        h('div', {
          class: 'eyes',
          style: eyeStyle(orangePos.value, { normalLeft: 112, centerLeft: '112px', peekLeft: '80px' }, { normalTop: 60, centerTop: '60px', peekTop: '55px' })
        }, [
          h(Pupil, { size: 12, maxDistance: 5, pupilColor: '#2D2D2D', isBlinking: isOrangeBlinking.value,
            forceLookX: props.loginSuccess ? 0 : ((props.passwordLength > 0 && props.showPassword) ? -5 : undefined),
            forceLookY: props.loginSuccess ? successLookY.value : ((props.passwordLength > 0 && props.showPassword) ? -4 : undefined) }),
          h(Pupil, { size: 12, maxDistance: 5, pupilColor: '#2D2D2D', isBlinking: isOrangeBlinking.value,
            forceLookX: props.loginSuccess ? 0 : ((props.passwordLength > 0 && props.showPassword) ? -5 : undefined),
            forceLookY: props.loginSuccess ? successLookY.value : ((props.passwordLength > 0 && props.showPassword) ? -4 : undefined) }),
        ]),
        h('div', {
          class: ['orange-mouth-shape', { 'orange-mouth-shape--typing': typing.value, 'orange-mouth-shape--sad': sad.value, 'orange-mouth-shape--happy': happy.value }],
          style: mouthStyle(orangePos.value, { normalLeft: 126, centerLeft: '126px', peekLeft: '94px' }, { normalTop: 92, centerTop: '92px', peekTop: '87px' })
        })
      ]),

      // 黄色 - 前右
      h('div', {
        ref: yellowRef,
        class: ['character', 'yellow-character', { 'entrance-complete': hasEntered.value }],
        style: { left: '310px', width: '140px', height: '230px', backgroundColor: '#E8D754', borderRadius: '70px 70px 0 0', zIndex: 4, ...yellowBody.value }
      }, [
        h('div', {
          class: 'eyes',
          style: eyeStyle(yellowPos.value, { normalLeft: 52, centerLeft: '52px', peekLeft: '20px' }, { normalTop: 40, centerTop: '40px', peekTop: '35px' })
        }, [
          h(Pupil, { size: 12, maxDistance: 5, pupilColor: '#2D2D2D', isBlinking: isYellowBlinking.value,
            forceLookX: props.loginSuccess ? 0 : ((props.passwordLength > 0 && props.showPassword) ? -5 : undefined),
            forceLookY: props.loginSuccess ? successLookY.value : ((props.passwordLength > 0 && props.showPassword) ? -4 : undefined) }),
          h(Pupil, { size: 12, maxDistance: 5, pupilColor: '#2D2D2D', isBlinking: isYellowBlinking.value,
            forceLookX: props.loginSuccess ? 0 : ((props.passwordLength > 0 && props.showPassword) ? -5 : undefined),
            forceLookY: props.loginSuccess ? successLookY.value : ((props.passwordLength > 0 && props.showPassword) ? -4 : undefined) }),
        ]),
        h('div', {
          class: 'yellow-mouth-wrapper',
          style: { left: ((props.passwordLength > 0 && props.showPassword) ? '10px' : `${40 + yellowPos.value.faceX}px`), top: ((props.passwordLength > 0 && props.showPassword) ? '88px' : `${88 + yellowPos.value.faceY}px`) }
        }, [
          h('svg', { width: 80, height: 20, viewBox: '0 0 80 20' }, [
            h('path', {
              class: ['yellow-mouth-path', { 'yellow-mouth-path--wavy': sad.value, 'yellow-mouth-path--happy': happy.value }],
              stroke: '#2D2D2D', 'stroke-width': 3, fill: 'none', 'stroke-linecap': 'round'
            })
          ])
        ])
      ]),
    ]);
  }
});

/* 暴露到全局（兼容旧用法） */
if (typeof window !== 'undefined') {
  window.AuthLib = { AnimatedCharacters, createApp, ref, computed, watch, onMounted, onUnmounted, defineComponent };
}

/* ES Module 导出 */
export { AnimatedCharacters, createApp, ref, computed, watch, onMounted, onUnmounted, defineComponent };
