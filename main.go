package main

import (
	"cmp"
	"encoding/json/v2"
	"fmt"
	"net/http"
	"slices"

	spotraygo "github.com/chetan0402/SpotRay-go"
	rl "github.com/gen2brain/raylib-go/raylib"
)

const baseURL = "http://127.0.0.1:8080/api/v2"

const torrentInfoURL = baseURL + "/torrents/info"

const FONT = "RobotoMonoNerdFont-Medium.ttf"

type Torrent struct {
	Hash                string  `json:"hash"`
	Name                string  `json:"name"`
	TimeActive          int     `json:"time_active"`
	SeedRatio           float32 `json:"ratio"`
	SavePath            string  `json:"save_path"`
	MaxInactiveSeedTime int     `json:"max_inactive_seed_time"`
	MaxRatio            int     `json:"max_ratio"`
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
		},
		Font: FONT,
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
