import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;

//! Application entry point. A watch face is an AppBase whose initial view is a WatchUi.WatchFace.
class SteampunkNixieApp extends Application.AppBase {

    function initialize() {
        AppBase.initialize();
    }

    //! Returns the watch face view plus its delegate.
    function getInitialView() as [WatchUi.Views] or [WatchUi.Views, WatchUi.InputDelegates] {
        return [new SteampunkNixieView(), new SteampunkNixieDelegate()];
    }
}

//! Watch-face delegate. onPowerBudgetExceeded fires when partial updates have blown the device's
//! power budget — on the Venu Sq 2 that is the burn-in protection talking, and partial updates
//! stop for the rest of the app's life if it trips.
class SteampunkNixieDelegate extends WatchUi.WatchFaceDelegate {

    function initialize() {
        WatchFaceDelegate.initialize();
    }

    function onPowerBudgetExceeded(powerInfo as WatchUi.WatchFacePowerInfo) as Void {
        // WatchFacePowerInfo exposes executionTimeAverage / executionTimeLimit as PROPERTIES.
        System.println("power budget exceeded: executionTimeAverage="
                       + powerInfo.executionTimeAverage
                       + " limit=" + powerInfo.executionTimeLimit);
    }
}
