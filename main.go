package main

import (
	"cmp"
	"encoding/json/v2"
	"fmt"
	"net/http"
	"net/url"
	"slices"
	"strings"

	spotraygo "github.com/chetan0402/SpotRay-go"
	rl "github.com/gen2brain/raylib-go/raylib"
)

const baseURL = "http://127.0.0.1:8080/api/v2"

const (
	torrentInfoURL          = baseURL + "/torrents/info"
	torrentSetShareLimitURL = baseURL + "/torrents/setShareLimits"
)

const FONT = "RobotoMonoNerdFont-Medium.ttf"

type Torrent struct {
	Hash                string  `json:"hash"`
	Name                string  `json:"name"`
	TimeActive          int     `json:"time_active"`
	SeedRatio           float32 `json:"ratio"`
	SavePath            string  `json:"save_path"`
	MaxInactiveSeedTime int     `json:"max_inactive_seed_time"`
	MaxRatio            float32 `json:"max_ratio"`
	MaxSeedingTime      int     `json:"max_seeding_time"`
	SeedingTime         int     `json:"seeding_time"`
	eta                 int     // in seconds
}

var SORTBYACTIVETIME bool = true

func getTorrents() []Torrent {
	resp, err := http.Get(torrentInfoURL)
	if err != nil {
		panic(err)
	}
	var torrents []Torrent
	if err := json.UnmarshalRead(resp.Body, &torrents); err != nil {
		panic(err)
	}
	for i, v := range torrents {
		torrents[i].eta = min(int((float32(v.TimeActive)/(v.SeedRatio+1e-9))*(1-v.SeedRatio)), 60*v.MaxSeedingTime-v.SeedingTime)
	}
	return torrents
}

func setSharingLimits(hash string, ratio float32, active int, inactive int) {
	data := url.Values{}
	data.Set("hashes", hash)
	data.Set("ratioLimit", fmt.Sprintf("%f", ratio))
	data.Set("seedingTimeLimit", fmt.Sprintf("%d", active))
	data.Set("inactiveSeedingTimeLimit", fmt.Sprintf("%d", inactive))
	resp, err := http.Post(torrentSetShareLimitURL, "application/x-www-form-urlencoded", strings.NewReader(data.Encode()))
	if err != nil {
		panic(err)
	}
	if resp.StatusCode >= 400 {
		panic(resp.StatusCode)
	}
}

func getMainState() *spotraygo.State {
	torrents := getTorrents()
	if SORTBYACTIVETIME {
		slices.SortFunc(torrents, func(a, b Torrent) int {
			return cmp.Compare(a.TimeActive, b.TimeActive)
		})
	} else {
		slices.SortFunc(torrents, func(a, b Torrent) int {
			if a.eta < 0 && b.eta < 0 {
				return cmp.Compare(a.TimeActive, b.TimeActive)
			}
			if a.eta < 0 {
				return 1
			}
			if b.eta < 0 {
				return -1
			}
			return cmp.Compare(a.eta, b.eta)
		})
	}
	opts := make([]spotraygo.Item, len(torrents))
	for i := range opts {
		opts[i].Key = torrents[i].Hash
		opts[i].Value = fmt.Sprintf("%-100.100s|%.3f|%s", torrents[i].Name, torrents[i].SeedRatio, formatDuration(torrents[i].eta))
	}
	return &spotraygo.State{
		Options: opts,
		Keybinds: map[int32]func(*spotraygo.App){
			rl.KeyTab: func(a *spotraygo.App) {
				SORTBYACTIVETIME = !SORTBYACTIVETIME
				a.SetState(getMainState())
			},
			rl.KeyRight: func(a *spotraygo.App) {
				k := a.GetSelectedKey()
				for i := range torrents {
					if torrents[i].Hash == k {
						a.SetState(getInfoState(k, torrents[i].Name, torrents[i].MaxRatio, torrents[i].MaxSeedingTime))
						return
					}
				}
				panic("didn't find the hash in list")
			},
		},
		Font: FONT,
	}
}

func getInfoState(hash string, name string, ratio float32, active int) *spotraygo.State {
	return &spotraygo.State{
		Options: []spotraygo.Item{
			{Key: "", Value: name},
			{Key: "", Value: fmt.Sprintf("Ratio: %f", ratio)},
			{Key: "", Value: fmt.Sprintf("Active: %s", formatDuration(60*active))},
			{Key: "no", Value: "Set no limit"},
			{Key: "global", Value: "Set global limit"},
			{Key: "airing", Value: "Set airing limit"},
		},
		Keybinds: map[int32]func(*spotraygo.App){
			rl.KeyLeft: func(a *spotraygo.App) {
				a.SetState(getMainState())
			},
			rl.KeyEnter: func(a *spotraygo.App) {
				k := a.GetSelectedKey()
				switch k {
				case "no":
					setSharingLimits(hash, -1.0, -1, -1)
				case "global":
					setSharingLimits(hash, -2.0, -2, -2)
				case "airing":
					setSharingLimits(hash, 1.0, 4000, -1)
				}
				a.SetState(getMainState())
			},
		},
	}
}

func main() {
	app := spotraygo.NewApp()
	app.SetState(getMainState())
	app.Start()
}

func formatDuration(seconds int) string {
	if seconds <= 0 {
		return "inf"
	}

	const (
		minute = 60
		hour   = 3600
		day    = 86400
		year   = 31536000
	)

	switch {
	case seconds >= year:
		years := seconds / year
		days := (seconds % year) / day
		return fmt.Sprintf("%dy %dd", years, days)
	case seconds >= day:
		days := seconds / day
		hours := (seconds % day) / hour
		return fmt.Sprintf("%dd %dh", days, hours)
	case seconds >= hour:
		hours := seconds / hour
		minutes := (seconds % hour) / minute
		return fmt.Sprintf("%dh %dm", hours, minutes)
	case seconds >= minute:
		minutes := seconds / minute
		secs := seconds % minute
		return fmt.Sprintf("%dm %ds", minutes, secs)
	default:
		return fmt.Sprintf("%ds", seconds)
	}
}
