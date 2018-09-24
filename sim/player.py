import logging
import numpy as np


log = logging.getLogger(__name__)


class Player(object):

    def __init__(self, env, connection, segments, logic, traffictrace):
        self._env = env
        self._connection = connection
        self._segments = segments
        self._logic = logic
        self._traffictrace = traffictrace
        self._timeSinceLastSwitch = []

        self._buffer_level = 0
        self._buffer_level_segments = 0
        self._buffer_heap = []
        self._playback_position = 0
        self._playtimeLeft = 0

        self._quality_sum = 0

        metrics_keys = ['stalling_time', 'sum_stalling', 'sum_switches',
                        'average_playback_quality', 'startup_stalling_time',
                        'startup_sum_stalling', 'startup_sum_switches', 'endphase_stalling_time'
                        'endphase_sum_stalling', 'endphase_sum_switches',
                        'critbuff_time', 'lowbuff_time', 'riskybuff_time',
                        'healthybuff_time', 'bloatedbuff_time', 'jumps_1_levels',
                        'jumps_2_levels', 'jumps_3_levels', 'jumps_4_levels']

        self._metrics = {mk: 0 for mk in metrics_keys}

        self._next_segment_ev = None

        self._log_stallings = self._env.logdir.new('sim_stallings', ['time', 'playback_position', 'duration'])
        self._log_decisions = self._env.logdir.new('sim_decisions', ['segment', 'quality_level'])
        self._log_buffer = self._env.logdir.new('sim_buffer', ['time', 'playback_position', 'buffer_level'])
        self._log_metrics = self._env.logdir.new('sim_metrics', self._metrics)

    def run(self):

        log.debug("%.3fs: Player startup" % self._env.now)

        # Log the currently empty buffer
        self._log_buffer.write({'time': self._env.now, 'playback_position': self._playback_position,
                                'buffer_level': self._buffer_level})

        log.debug("%.3fs: Downloading first segment in chosen quality." % self._env.now)

        # Begin playback
        buffer_below_thresh_critbuff = 0
        time_below_thresh_critbuff = 0

        buffer_below_thresh_lowbuff = 0
        time_below_thresh_lowbuff = 0

        buffer_below_thresh_riskybuff = 0
        time_below_thresh_riskybuff = 0

        buffer_below_thresh_healthybuff = 0
        time_below_thresh_healthybuff = 0

        buffer_below_thresh_bloatedbuff = 0
        time_below_thresh_bloatedbuff = 0
        decision_memory = 0 #self._logic.decide(0)
        decision = decision_memory
        self._timeSinceLastSwitch.append(0)

        self._env.process(self._play())

        # Download the next segments based on the logic.
        for i in range(self._segments.shape[0]):#-1

            if i == 0:
                self._logic.calculatefeature(i, self._env.now, self._buffer_level_segments, self._buffer_level,
                                             self._traffictrace, self._timeSinceLastSwitch, self._segments, 0)

                decision, bufferDelay = self._logic.decide(i)  # +1
                decision_memory = decision
            else:
                self._logic.calculatefeature(i, self._env.now, self._buffer_level_segments, self._buffer_level,
                                             self._traffictrace, self._timeSinceLastSwitch, self._segments, self._segments[i - 1][decision])
                decision, bufferDelay = self._logic.decide(i)

            if decision != decision_memory:
                self._metrics['sum_switches'] += 1
                self._timeSinceLastSwitch.append(1)

                if self._playtimeLeft >= self._segments.shape[0]-30:
                    self._metrics['startup_sum_switches'] += 1
                elif self._playtimeLeft <= 30:
                    self._metrics['endphase_sum_switches'] += 1

                if np.abs(decision - decision_memory) == 1:
                    self._metrics['jumps_1_levels'] += 1
                elif np.abs(decision - decision_memory) == 2:
                    self._metrics['jumps_2_levels'] += 1
                elif np.abs(decision - decision_memory) == 3:
                    self._metrics['jumps_3_levels'] += 1
                elif np.abs(decision - decision_memory) == 4:
                    self._metrics['jumps_4_levels'] += 1
            else:
                self._timeSinceLastSwitch.append(0)


            if self._buffer_level < 5 and buffer_below_thresh_critbuff == 0:
                buffer_below_thresh_critbuff = 1
                time_below_thresh_critbuff = self._env.now
            elif self._buffer_level < 5 and buffer_below_thresh_critbuff == 1:
                self._metrics['critbuff_time'] += (self._env.now - time_below_thresh_critbuff)
                time_below_thresh_critbuff = self._env.now
            elif self._buffer_level >= 5 and buffer_below_thresh_critbuff == 1:
                self._metrics['critbuff_time'] += (self._env.now - time_below_thresh_critbuff)
                buffer_below_thresh_critbuff = 0

            if self._buffer_level < 10 and buffer_below_thresh_lowbuff == 0:
                buffer_below_thresh_lowbuff = 1
                time_below_thresh_lowbuff = self._env.now
            elif self._buffer_level < 10 and buffer_below_thresh_lowbuff == 1:
                self._metrics['lowbuff_time'] += (self._env.now - time_below_thresh_lowbuff)
                time_below_thresh_lowbuff = self._env.now
            elif self._buffer_level >= 10 and buffer_below_thresh_lowbuff == 1:
                self._metrics['lowbuff_time'] += (self._env.now - time_below_thresh_lowbuff)
                buffer_below_thresh_lowbuff = 0

            if self._buffer_level < 15 and buffer_below_thresh_riskybuff == 0:
                buffer_below_thresh_riskybuff = 1
                time_below_thresh_riskybuff = self._env.now
            elif self._buffer_level < 15 and buffer_below_thresh_riskybuff == 1:
                self._metrics['riskybuff_time']+= (self._env.now - time_below_thresh_riskybuff)
                time_below_thresh_riskybuff = self._env.now
            elif self._buffer_level >= 15 and buffer_below_thresh_riskybuff == 1:
                self._metrics['riskybuff_time']+= (self._env.now - time_below_thresh_riskybuff)
                buffer_below_thresh_riskybuff = 0


            if self._buffer_level >= 15 and buffer_below_thresh_healthybuff == 0:
                buffer_below_thresh_healthybuff = 1
                time_below_thresh_healthybuff = self._env.now
            elif self._buffer_level >= 15 and buffer_below_thresh_healthybuff == 1:
                self._metrics['healthybuff_time'] += (self._env.now - time_below_thresh_healthybuff)
                time_below_thresh_healthybuff = self._env.now
            elif self._buffer_level < 15 and buffer_below_thresh_healthybuff == 1:
                self._metrics['healthybuff_time'] += (self._env.now - time_below_thresh_healthybuff)
                buffer_below_thresh_healthybuff = 0

            if self._buffer_level > 60 and buffer_below_thresh_bloatedbuff == 0:
                buffer_below_thresh_bloatedbuff = 1
                time_below_thresh_bloatedbuff = self._env.now
            elif self._buffer_level > 60 and buffer_below_thresh_bloatedbuff == 1:
                self._metrics['bloatedbuff_time'] += (self._env.now - time_below_thresh_bloatedbuff)
                time_below_thresh_bloatedbuff = self._env.now
            elif self._buffer_level <= 60 and buffer_below_thresh_bloatedbuff == 1:
                self._metrics['bloatedbuff_time'] += (self._env.now - time_below_thresh_bloatedbuff)
                buffer_below_thresh_bloatedbuff = 0

            decision_memory = decision

            self._quality_sum += decision

            self._log_decisions.write({'segment': i+1, 'quality_level': decision})

            yield self._env.process(self._connection.download(self._segments[i][decision], bufferDelay))

            self._buffer_level += 1
            self._buffer_level_segments += self._segments[i][decision]
            self._buffer_heap.append(self._segments[i][decision])

            if self._next_segment_ev is not None:
                self._next_segment_ev.succeed()

    def _play(self):

        self._playtimeLeft = self._segments.shape[0]

        # Set Playout delay
        yield self._env.process(self._connection.initialdelay(self._segments[0][4]))

        while self._playtimeLeft > 0:

            self._log_buffer.write({'time': self._env.now, 'playback_position': self._playback_position,
                                    'buffer_level': self._buffer_level})

            if self._buffer_level > 0:

                # Place a segment into the playout buffer (= Decrease buffer level by 1s)
                self._buffer_level -= 1
                self._buffer_level_segments -= self._buffer_heap.pop(0)

                # Show the segment to the user
                yield self._env.timeout(1)

                self._playback_position += 1
                self._playtimeLeft -= 1

                log.debug("%.3fs: Playback status: at %.1fs. Buffer level: %.1fs" % (self._env.now,
                                                                                     self._playback_position,
                                                                                     self._buffer_level))
            else:

                start = self._env.now

                log.debug("%.3fs: Stalling." % self._env.now)

                self._next_segment_ev = self._env.event()

                yield self._next_segment_ev

                stalling_duration = self._env.now - start

                self._metrics['stalling_time'] += stalling_duration
                self._metrics['sum_stalling'] += 1

                if self._playtimeLeft >= self._segments.shape[0]-60:
                    self._metrics['startup_stalling_time'] += stalling_duration
                    self._metrics['startup_sum_stalling'] += 1
                elif self._playtimeLeft <= 60:
                    self._metrics['endphase_stalling_time'] += stalling_duration
                    self._metrics['endphase_sum_stalling'] += 1

                log.debug("%.3fs: Stalling took %.3fs." % (self._env.now, stalling_duration))

                self._log_stallings.write({'time': self._env.now,
                                           'playback_position': self._playback_position,
                                           'duration': stalling_duration})

                self._next_segment_ev = None

        self._metrics['average_quality'] = self._quality_sum / len(self._segments)

        self._log_metrics.write(self._metrics)
